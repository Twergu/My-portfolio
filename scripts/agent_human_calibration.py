"""Paid Verifier calibration against actual human-reviewed frozen candidates."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from backend.config import ROOT, environment_settings
from backend.telemetry import Metrics
from backend.verification import BASELINE, verify_claims
from scripts.agent_diagnose import RecordingProvider
from scripts.human_review_report import summarize


def run(output):
    output = Path(output)
    if output.exists():
        raise SystemExit("Preserve past runs; use a new report filename")
    data = json.loads((ROOT / "evals/agent-human-review-v1.json").read_text(encoding="utf-8"))
    annotations = json.loads((ROOT / "evals/agent-human-review-v1.annotations.json").read_text(encoding="utf-8"))
    review = summarize(data, annotations)
    if review["status"] != "reviewed":
        raise SystemExit("Complete actual human review and reference adjudication before scoring")
    settings = environment_settings().model_copy(
        update={"mode": "api", "verification_mode": "strict", "verification_strategy": "all"}
    )
    key = os.getenv("RAG_API_KEY")
    if not key:
        raise SystemExit("Configure RAG_API_KEY")
    labels = {r["id"]: r for r in annotations["cases"]}
    provider = RecordingProvider()
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Real Verifier API on eight human-reviewed candidate/evidence pairs. Offline calibration, not end-to-end Agent quality; constructed candidates include four intentional errors. Reviewer saw proposed references; not blind or independent adjudication. New threshold rule used these cases for development, so this is not a held-out test.",
        "dataset_sha256": review["dataset_sha256"],
        "reviewer": review["reviewer"],
        "model": settings.effective_verifier_model,
        "baseline_prompt": BASELINE,
        "cases": [],
        "model_calls": provider.records,
    }
    try:
        for row in data["cases"]:
            metrics = Metrics()
            claim = {
                "claim_index": 1,
                "text": row["candidate"],
                "cited_passages": [
                    {
                        "source_id": 1,
                        "quote": row["source"],
                        "text": row["source"],
                        "kind": "document",
                        "provenance": "retrieved",
                        "metadata": {"policy_status": "current", "effective_from": "2026-01-01"},
                    },
                    {
                        "source_id": 2,
                        "quote": row["question"],
                        "text": row["question"],
                        "kind": "user",
                        "provenance": "self_report",
                        "metadata": {},
                    },
                ],
            }
            result = {"id": row["id"], "human_supported": labels[row["id"]]["all_claims_supported"], "claim": claim}
            try:
                verdict = verify_claims(
                    row["question"], [claim], settings, key, provider, metrics, prompt="baseline", agent_mode=True
                )[0]
                result.update(
                    verdict=verdict.model_dump(), matches_human=verdict.supported == result["human_supported"]
                )
            except Exception as exc:
                result.update(error_type=type(exc).__name__, matches_human=False)
            result["usage"] = metrics.as_dict()
            report["cases"].append(result)
            save(report, output)
            print(row["id"], result["matches_human"], flush=True)
    finally:
        provider.close()
        save(report, output)


def save(report, output):
    rows = report["cases"]
    pairs = [(r["human_supported"], r.get("verdict", {}).get("supported")) for r in rows]
    tp = sum(a is True and b is True for a, b in pairs)
    fp = sum(a is False and b is True for a, b in pairs)
    fn = sum(a is True and b is False for a, b in pairs)
    tn = sum(a is False and b is False for a, b in pairs)
    errors = sum(b is None for _, b in pairs)
    scorable = len(rows) == 8 and errors == 0
    report["summary"] = {
        "completed": len(rows),
        "expected": 8,
        "complete": len(rows) == 8,
        "errors": errors,
        "agreement": sum(r["matches_human"] for r in rows) / 8 if len(rows) == 8 else None,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": tp / (tp + fp) if scorable and tp + fp else None,
        "recall": tp / (tp + fn) if scorable and tp + fn else None,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(
        "# Human-reviewed Verifier calibration\n\n"
        + report["scope"]
        + "\n\n```json\n"
        + json.dumps(report["summary"], indent=2)
        + "\n```\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if not args.live:
        parser.error("--live permits paid Verifier requests on the reviewed fictional data")
    run(args.output)
