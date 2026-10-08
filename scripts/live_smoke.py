"""Small real PDF -> embedding -> LLM -> evidence smoke, using configured API.

This command intentionally makes paid API calls when RAG_API_KEY is present.
No key: writes a blocked report and exits 2. No simulated success is reported.
"""

import argparse
import io
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import environment_settings


def fictional_pdf():
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(60, 760, "Aster Labs - fictional smoke-test handbook")
    pdf.drawString(60, 720, "Employees receive 18 days of annual leave per year.")
    pdf.drawString(60, 700, "The direct manager approves annual leave requests.")
    pdf.showPage()
    pdf.drawString(60, 760, "Travel expense policy - fictional test data")
    pdf.drawString(60, 720, "The hotel reimbursement cap is JPY 14500 per night.")
    pdf.drawString(60, 700, "Submit receipts within 12 calendar days after returning.")
    pdf.save()
    return buffer.getvalue()


def write(report, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    message = report.get("reason", "See the recorded checks and provider metrics in the JSON report.")
    output.with_suffix(".md").write_text(
        "\n".join(
            [
                "# Real API smoke test",
                "",
                f"Status: **{report['status']}**",
                "",
                message,
                "",
                "Only a generated fictional two-page PDF is submitted. Customer documents and the application data directory are not used.",
                "",
                "A passed run requires document indexing, a generated answer, exact source quotation checks, model entailment verification, a page-2 citation, and the expected hotel amount.",
                "",
                "This is connectivity and pipeline evidence for one fictional question, not a model-quality benchmark.",
                "",
                "Cost is an estimate from reported token usage and configured prices. Missing usage/prices remain unknown.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def run(output):
    settings = environment_settings().model_copy(
        update={"mode": "api", "search_mode": "exact", "verification_mode": "strict"}
    )
    key = os.getenv("RAG_API_KEY", "")
    report = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "blocked",
        "chat_model": settings.chat_model,
        "embedding_model": settings.embedding_model,
        "verifier_model": settings.effective_verifier_model,
        "real_api_calls_attempted": False,
        "checks": {},
        "operations": [],
        "cost_usd": None,
    }
    if not key:
        report["reason"] = (
            "RAG_API_KEY is not configured. No real API calls were attempted; provide a key in the local environment and rerun this command."
        )
        write(report, output)
        print("BLOCKED: RAG_API_KEY is missing; report written, no API call made.")
        return 2
    from fastapi.testclient import TestClient

    from backend.main import create_app

    started = time.perf_counter()
    try:
        with tempfile.TemporaryDirectory(prefix="rag-live-smoke-") as folder:
            # Explicit empty database_url chooses a fresh SQLite database even if
            # the application environment configures a production PostgreSQL URL.
            app = create_app(Path(folder), database_url="")
            with TestClient(app, base_url="http://localhost") as client:
                response = client.put("/api/settings", json=settings.model_dump() | {"api_key": key})
                if response.status_code != 200:
                    raise RuntimeError("Cannot configure temporary smoke-test application")
                response = client.post(
                    "/api/documents", files={"file": ("aster-smoke.pdf", fictional_pdf(), "application/pdf")}
                )
                if response.status_code != 202:
                    raise RuntimeError("Cannot upload fictional PDF")
                doc_id = response.json()["id"]
                app.state.knowledge.wait_for_jobs()
                document = app.state.knowledge.store.document(doc_id)
                report["checks"]["indexed"] = document["status"] == "ready"
                report["checks"]["physical_pages"] = document["pages"] == 2
                if not report["checks"]["indexed"]:
                    raise RuntimeError("Real API indexing failed")
                response = client.post(
                    "/api/chat",
                    json={
                        "question": "What is the hotel reimbursement cap per night?",
                        "document_ids": [doc_id],
                        "language": "en",
                    },
                )
                if response.status_code != 200:
                    raise RuntimeError("Real API answer request failed")
                result = response.json()
                report["checks"].update(
                    {
                        "generated_answer": result["status"] == "answered",
                        "expected_amount": "14500" in result["answer"].replace(",", ""),
                        "page_2_citation": any(source["page"] == 2 for source in result["sources"]),
                        "grounded_claims": result.get("support", {}).get("all_supported") is True,
                        "original_pdf_available": client.get(f"/api/documents/{doc_id}/file").content.startswith(
                            b"%PDF-"
                        ),
                    }
                )
                report["answer"] = result["answer"]
                report["claims"] = result.get("claims", [])
                report["support"] = result.get("support")
                report["status"] = "passed" if all(report["checks"].values()) else "failed"
                report["reason"] = (
                    "Real embedding, generation, and entailment-verification requests completed and all smoke assertions passed."
                    if report["status"] == "passed"
                    else "The real pipeline ran, but one or more smoke assertions failed."
                )
                report["operations"] = list(app.state.knowledge.measurements)
    except Exception as exc:
        report["status"] = "failed"
        # Exception strings may contain provider data; record only the type.
        report["reason"] = (
            f"Live smoke did not complete ({type(exc).__name__}). Check the configured endpoint, model compatibility, and API access; no success is claimed."
        )
        if "app" in locals():
            report["operations"] = list(app.state.knowledge.measurements)
    report["elapsed_ms"] = (time.perf_counter() - started) * 1000
    report["real_api_calls_attempted"] = any(
        operation["metrics"].get("attempt_count", 0) > 0 for operation in report["operations"]
    )
    costs = [operation["metrics"].get("cost_usd") for operation in report["operations"]]
    report["cost_usd"] = sum(costs) if costs and all(cost is not None for cost in costs) else None
    write(report, output)
    print(f"{report['status'].upper()}: {Path(output).with_suffix('.md')}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evals" / "reports" / "live-api-smoke")
    sys.exit(run(parser.parse_args().output))
