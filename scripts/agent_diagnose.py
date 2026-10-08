"""Opt-in diagnostics on fictional policies; never enable raw-prompt logging in HTTP routes."""

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from backend.config import ROOT, environment_settings
from backend.main import create_app
from backend.providers import OpenAICompatibleProvider
from scripts.agent_live_smoke import make_pdf

QUESTION = "通勤補助の申請条件を確認したいです。判断に必要な情報があれば質問してください。"
REPLY = "フルタイム勤務で、週3日出社しています。雇用形態申告書と出社勤務スケジュールを提出できます。"


class RecordingProvider(OpenAICompatibleProvider):
    """Explicit offline opt-in: store prompts/outputs, never keys, headers or embeddings."""

    def __init__(self):
        super().__init__()
        self.records = []

    def chat(self, settings, api_key, messages, *args, **kwargs):
        record = {"role": kwargs.get("role", "generator"), "messages": messages}
        self.records.append(record)
        try:
            raw = super().chat(settings, api_key, messages, *args, **kwargs)
            record["output"] = raw
            return raw
        except Exception as exc:
            record["error_type"] = type(exc).__name__
            raise


def run(output, repeats):
    provider = RecordingProvider()
    config = environment_settings().model_copy(
        update={
            "mode": "api",
            "retrieval_mode": "hybrid",
            "reranker_mode": "off",
            "top_k": 3,
            "verification_mode": "strict",
            "verification_strategy": "all",
            "verifier_prompt": "baseline",
            "search_mode": "exact",
            "chunk_size": 900,
            "chunk_overlap": 0,
        }
    )
    if not os.getenv("RAG_API_KEY"):
        raise SystemExit("API key missing")
    previous = os.environ.get("RAG_AUTH_MODE")
    os.environ["RAG_AUTH_MODE"] = "required"
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Real API on fictional policies; raw prompts/outputs explicitly recorded offline",
        "settings": config.model_dump(),
        "cases": [],
        "model_calls": provider.records,
    }
    service = None
    try:
        with tempfile.TemporaryDirectory(prefix="agent-diagnosis-") as directory:
            app = create_app(Path(directory), database_url="", provider=provider)
            service = app.state.knowledge
            service.settings = config
            _, token = service.store.provision_user("diagnostic-reviewer", ["admin"])
            fixture = json.loads((ROOT / "evals/agent-workflows.json").read_text(encoding="utf-8"))
            with TestClient(app) as client:
                client.headers["Authorization"] = "Bearer " + token
                response = client.post(
                    "/api/documents",
                    files={"file": ("fictional-policy.pdf", make_pdf(fixture["pages"]), "application/pdf")},
                )
                response.raise_for_status()
                doc_id = response.json()["id"]
                service.wait_for_jobs()
                if service.store.document(doc_id)["status"] != "ready":
                    raise RuntimeError("Indexing failed")
                client.put(
                    f"/api/documents/{doc_id}/metadata",
                    json={"policy_status": "current", "effective_from": "2026-01-01"},
                ).raise_for_status()
                for attempt in range(repeats):
                    start = len(provider.records)
                    first = client.post(
                        "/api/agent", json={"question": QUESTION, "language": "ja", "document_ids": [doc_id]}
                    )
                    first.raise_for_status()
                    first = first.json()
                    final = first
                    if first["status"] == "needs_input":
                        final = client.post(f"/api/agent/{first['task_id']}/reply", json={"question": REPLY})
                        final.raise_for_status()
                        final = final.json()
                    first.pop("task_id", None)
                    final.pop("task_id", None)
                    report["cases"].append(
                        {
                            "attempt": attempt + 1,
                            "call_start": start,
                            "call_end": len(provider.records),
                            "first": first,
                            "final": final,
                        }
                    )
                    print(
                        f"Attempt {attempt + 1}: {first['status']} -> {final['status']}; {final.get('support', {}).get('verified_claims')}/{final.get('support', {}).get('total_claims')}",
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
        report["operations"] = list(service.measurements) if service else []
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--repeats", type=int, choices=range(1, 4), default=2)
    parser.add_argument("--output", default="reports/agent-hardening/p0-before.json")
    args = parser.parse_args()
    if not args.live:
        parser.error("--live explicitly permits paid requests and diagnostic recording on fictional data")
    run(args.output, args.repeats)
