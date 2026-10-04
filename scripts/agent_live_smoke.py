"""Opt-in real PDF indexing + Agent retrieval/tools/generation/verification smoke."""

import argparse
import io
import json
import os
import tempfile
import textwrap
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from backend.config import ROOT, environment_settings
from backend.main import create_app


def make_pdf(pages):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    for index, content in enumerate(pages, 1):
        pdf.drawString(50, 780, f"Fictional Agent test policy - page {index}")
        for line, text in enumerate(textwrap.wrap(content, width=90)):
            pdf.drawString(50, 745 - line * 18, text)
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def run(output):
    fixture = json.loads((ROOT / "evals/agent-workflows.json").read_text(encoding="utf-8"))
    settings = environment_settings().model_copy(
        update={
            "mode": "api",
            "retrieval_mode": "hybrid",
            "reranker_mode": "off",
            "verification_mode": "strict",
            "verification_strategy": "all",
            "search_mode": "exact",
            "top_k": 3,
            "chunk_size": 900,
            "chunk_overlap": 0,
        }
    )
    key = os.getenv("RAG_API_KEY", "")
    if not key:
        raise SystemExit("RAG_API_KEY is missing; no API calls were made.")
    report = {
        "dataset": fixture["version"],
        "dataset_provenance": fixture["provenance"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "settings": settings.model_dump(),
        "scope": "Real Embedding, Planner, Generator, Verifier; real isolated SQLite retrieval, deterministic math/dates, explicitly mock workweek calendar. No customer documents or external writes.",
        "status": "failed",
        "cases": [],
        "operations": [],
    }
    service = None
    previous_auth = os.environ.get("RAG_AUTH_MODE")
    os.environ["RAG_AUTH_MODE"] = "required"
    try:
        with tempfile.TemporaryDirectory(prefix="knowbase-agent-live-") as directory:
            app = create_app(Path(directory), database_url="")
            service = app.state.knowledge
            service.settings, service.api_key = settings, key
            _, token = service.store.provision_user("fictional-reviewer", ["admin"])
            with TestClient(app, base_url="http://localhost") as client:
                client.headers["Authorization"] = "Bearer " + token
                upload = client.post(
                    "/api/documents",
                    files={"file": ("fictional-agent-policies.pdf", make_pdf(fixture["pages"]), "application/pdf")},
                )
                upload.raise_for_status()
                doc_id = upload.json()["id"]
                service.wait_for_jobs()
                if service.store.document(doc_id)["status"] != "ready":
                    raise RuntimeError("Fictional PDF indexing failed")
                client.put(
                    f"/api/documents/{doc_id}/metadata",
                    json={"policy_status": "current", "effective_from": "2026-01-01"},
                ).raise_for_status()
                for case in fixture["cases"]:
                    result = client.post(
                        "/api/agent",
                        json={
                            "question": case["question"],
                            "language": case["language"],
                            "document_ids": [doc_id],
                            "filters": {"policy_status": ["current"]},
                        },
                    )
                    result.raise_for_status()
                    first = result.json()
                    final = first
                    if first["status"] == "needs_input" and case.get("reply"):
                        result = client.post(f"/api/agent/{first['task_id']}/reply", json={"question": case["reply"]})
                        result.raise_for_status()
                        final = result.json()
                    tools = {step.get("tool") for step in final.get("trace", []) if step["event"] == "tool_completed"}
                    checks = {
                        "answered": final["status"] == "answered",
                        "grounded": final.get("support", {}).get("all_supported") is True,
                        "expected_tools": set(case["tools"]) <= tools,
                        "no_external_action": final.get("evidence_notices", {}).get("actions_executed") is False,
                    }
                    if case.get("expected_value"):
                        checks["expected_tool_value"] = any(
                            case["expected_value"] in json.dumps(source.get("metadata", {}).get("result", {}))
                            for source in final.get("sources", [])
                            if source.get("kind") == "tool"
                        )
                    if case.get("requires_clarification"):
                        checks["clarified"] = first["status"] == "needs_input"
                    if case.get("requires_mock_label"):
                        checks["mock_disclosed"] = final.get("evidence_notices", {}).get("uses_mock_data") is True
                    row = {
                        "id": case["id"],
                        "checks": checks,
                        "passed": all(checks.values()),
                        "first": first,
                        "final": final,
                    }
                    # Task handles are ephemeral capabilities; reports do not need them.
                    for response in (row["first"], row["final"]):
                        response.pop("task_id", None)
                    report["cases"].append(row)
                    print(f"{case['id']}: {final['status']}, checks={checks}", flush=True)
                report["status"] = "passed" if all(case["passed"] for case in report["cases"]) else "failed"
    except Exception as exc:
        report["error_type"] = type(exc).__name__
    finally:
        if previous_auth is None:
            os.environ.pop("RAG_AUTH_MODE", None)
        else:
            os.environ["RAG_AUTH_MODE"] = previous_auth
        if service:
            report["operations"] = list(service.measurements)
        costs = [operation["metrics"]["cost_usd"] for operation in report["operations"]]
        report["estimated_cost_usd"] = (
            round(sum(costs), 10) if costs and all(cost is not None for cost in costs) else None
        )
        path = Path(output).with_suffix(".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Agent live smoke: {report['status']}; estimated total USD {report['estimated_cost_usd']}.")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", default="reports/agent-stage2/live-smoke.json")
    args = parser.parse_args()
    if not args.live:
        parser.error("Pass --live to explicitly allow paid API calls.")
    raise SystemExit(run(args.output))
