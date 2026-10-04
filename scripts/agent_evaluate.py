"""Paid end-to-end Agent evaluation. Frozen scenarios; keep every failure and raw model output."""

import argparse
import hashlib
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from backend.config import ROOT, environment_settings
from backend.main import create_app
from backend.telemetry import Metrics
from evals.agent_metrics import markdown, score_case, summarize, task_usage, validate_dataset
from evals.judge import judge_answer
from scripts.agent_diagnose import RecordingProvider
from scripts.agent_live_smoke import make_pdf


def save(report, output):
    report["summary"] = summarize(report["cases"], report["expected_cases"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")


def run(output, label):
    path = ROOT / "evals/agent_dataset.json"
    dataset = json.loads(path.read_text(encoding="utf-8"))
    validate_dataset(dataset)
    settings = environment_settings().model_copy(
        update={
            "mode": "api",
            "verification_mode": "strict",
            "verification_strategy": "all",
            "verifier_prompt": "baseline",
            "retrieval_mode": "hybrid",
            "reranker_mode": "off",
            "search_mode": "exact",
            "chunk_size": 900,
            "chunk_overlap": 0,
            "top_k": 3,
        }
    )
    key, judge = os.getenv("RAG_API_KEY"), os.getenv("RAG_EVAL_JUDGE_MODEL")
    if not key or not judge:
        raise SystemExit("Configure RAG_API_KEY and RAG_EVAL_JUDGE_MODEL before --live evaluation")
    output = Path(output)
    if output.exists():
        raise SystemExit("Choose a new output filename; preserve previous successes and failures")
    provider = RecordingProvider()
    report = {
        "label": label,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.",
        "dataset_sha256": hashlib.sha256(json.dumps(dataset, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        "source_sha256": hashlib.sha256(
            b"".join(p.read_bytes() for p in sorted((ROOT / "backend").glob("*.py")))
        ).hexdigest(),
        "settings": settings.model_dump(),
        "judge_model": judge,
        "expected_cases": len(dataset["cases"]),
        "cases": [],
        "model_calls": provider.records,
    }
    previous = os.environ.get("RAG_AUTH_MODE")
    os.environ["RAG_AUTH_MODE"] = "required"
    service = None
    try:
        with tempfile.TemporaryDirectory(prefix="agent-evaluation-") as directory:
            app = create_app(Path(directory), database_url="", provider=provider)
            service = app.state.knowledge
            service.settings, service.api_key = settings, key
            _, token = service.store.provision_user("fictional-evaluator", ["admin"])
            with TestClient(app) as client:
                client.headers["Authorization"] = "Bearer " + token
                upload = client.post(
                    "/api/documents",
                    files={"file": ("agent-eval-policies.pdf", make_pdf(dataset["pages"]), "application/pdf")},
                )
                upload.raise_for_status()
                doc_id = upload.json()["id"]
                service.wait_for_jobs()
                if service.store.document(doc_id)["status"] != "ready":
                    raise RuntimeError("Indexing failed")
                client.put(
                    f"/api/documents/{doc_id}/metadata",
                    json={"policy_status": "current", "effective_from": "2026-01-01"},
                ).raise_for_status()
                gold = {
                    "documents": [
                        {"id": doc_id, "pages": [{"page": i, "text": t} for i, t in enumerate(dataset["pages"], 1)]}
                    ]
                }
                for case in dataset["cases"]:
                    row = {"id": case["id"], "contract": case, "turns": [], "call_start": len(provider.records)}
                    judgment, judge_metrics, pending = {}, Metrics(), None
                    measurements_start = len(service.measurements)
                    started = time.perf_counter()
                    try:
                        response = client.post(
                            "/api/agent",
                            json={
                                "question": case["question"],
                                "language": case["language"],
                                "document_ids": [doc_id],
                                "filters": {"policy_status": ["current"]},
                            },
                        )
                        response.raise_for_status()
                        first = response.json()
                        pending = first.pop("task_id", None)
                        row["turns"].append(first)
                        if first["status"] == "needs_input" and case.get("reply"):
                            response = client.post(f"/api/agent/{pending}/reply", json={"question": case["reply"]})
                            response.raise_for_status()
                            final = response.json()
                            pending = final.pop("task_id", None)
                            row["turns"].append(final)
                        row["application_wall_ms"] = (time.perf_counter() - started) * 1000
                        query = case | {
                            "question": case["question"]
                            + ("\nUser reply: " + case["reply"] if case.get("reply") else ""),
                            "relevance": [{"document_id": doc_id, "page": p} for p in case["gold_pages"]],
                        }
                        # Neither gold references nor Judge verdicts enter runtime planning/generation.
                        judge_metrics = Metrics()
                        judgment = judge_answer(
                            row["turns"][-1],
                            query,
                            gold,
                            settings,
                            key,
                            provider,
                            judge,
                            judge_metrics,
                            agent_mode=True,
                        )
                    except Exception as exc:
                        row["error_type"] = type(exc).__name__
                        row["application_wall_ms"] = (time.perf_counter() - started) * 1000
                    finally:
                        if pending:
                            client.delete(f"/api/agent/{pending}")
                        row["judgment"], row["judge_usage"] = judgment, judge_metrics.as_dict()
                        row["scores"] = score_case(case, row["turns"], judgment)
                        if row.get("error_type"):
                            row["scores"]["task_success"] = False
                        # Service's finally block records even failed paid calls.
                        operations = list(service.measurements)[measurements_start:]
                        row["operations"] = operations
                        row["usage"] = task_usage(operations)
                        row["call_end"] = len(provider.records)
                        report["cases"].append(row)
                        save(report, output)
                    print(
                        f"{case['id']}: {row['scores']['final_status']} planning={row['scores']['planning_success']} task={row['scores']['task_success']}",
                        flush=True,
                    )
    except Exception as exc:
        report["error_type"] = type(exc).__name__
        raise
    finally:
        if previous is None:
            os.environ.pop("RAG_AUTH_MODE", None)
        else:
            os.environ["RAG_AUTH_MODE"] = previous
        report["indexing_operations"] = (
            [o for o in service.measurements if o["operation"] != "agent"] if service else []
        )
        save(report, output)
    print(json.dumps(report["summary"], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", required=True)
    parser.add_argument("--label", default="baseline")
    args = parser.parse_args()
    if not args.live:
        parser.error("--live explicitly permits paid model requests and raw diagnostics on fictional data")
    run(args.output, args.label)
