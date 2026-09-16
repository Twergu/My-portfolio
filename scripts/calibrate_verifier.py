"""Blind verifier classification, label-free requests, resumable per-case reports."""

import argparse
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from backend.config import environment_settings
from backend.providers import ModelError, OpenAICompatibleProvider
from backend.telemetry import Metrics
from backend.verification import verify_claims
from evals.metrics import distribution


def classification(rows):
    good = [r for r in rows if r["predicted"] is not None]
    tp = sum(r["expected"] and r["predicted"] for r in good)
    fp = sum(not r["expected"] and r["predicted"] for r in good)
    fn = sum(r["expected"] and not r["predicted"] for r in good)
    tn = len(good) - tp - fp - fn
    return {
        "positive_class": "supported",
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "false_accept_rate": fp / (fp + tn) if fp + tn else None,
        "false_reject_rate": fn / (tp + fn) if tp + fn else None,
        "errors": len(rows) - len(good),
        "n": len(rows),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--split", choices=["dev", "test"], required=True)
    p.add_argument("--prompt", choices=["baseline", "calibrated"], required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    data = json.loads(Path("evals/claim_calibration.json").read_text(encoding="utf-8"))
    settings = environment_settings().model_copy(update={"mode": "api"})
    key = os.getenv("RAG_API_KEY", "")
    if not key:
        p.error("RAG_API_KEY is missing")
    identity = {
        "dataset_sha256": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest(),
        "model": settings.effective_verifier_model,
        "prompt": args.prompt,
        "split": args.split,
        "endpoint_sha256": hashlib.sha256(settings.base_url.encode()).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if args.output.exists():
        previous = json.loads(args.output.read_text(encoding="utf-8"))
        if previous["identity"] != identity:
            raise ValueError("Resume configuration mismatch")
        rows = previous["cases"]
    done = {r["id"] for r in rows}
    requested_count = sum(c["split"] == args.split for c in data["cases"])
    with OpenAICompatibleProvider() as provider:

        def run(case):
            metrics = Metrics()
            claim = {
                "claim_index": 1,
                "text": case["claim"],
                "cited_passages": [{"source_id": 1, "quote": case["evidence"], "text": case["evidence"]}],
            }
            predicted, reason, error = None, "", None
            try:
                verdict = verify_claims(
                    case["question"], [claim], settings, key, provider, metrics, prompt=args.prompt
                )[0]
                predicted, reason = verdict.supported, verdict.reason
            except (ModelError, ValueError) as exc:
                error = exc.code if isinstance(exc, ModelError) else "invalid_verdict"
            return {
                "id": case["id"],
                "category": case["category"],
                "language": case["language"],
                "expected": case["supported"],
                "predicted": predicted,
                "reason": reason,
                "error": error,
                "metrics": metrics.as_dict(),
            }

        with ThreadPoolExecutor(max_workers=2) as pool:
            for row in pool.map(run, [c for c in data["cases"] if c["split"] == args.split and c["id"] not in done]):
                rows.append(row)
                costs = [r["metrics"]["cost_usd"] for r in rows]
                report = {
                    "identity": identity,
                    "review_status": data["review_status"],
                    "status": "completed"
                    if len(rows) == requested_count and all(r["error"] is None for r in rows)
                    else "incomplete",
                    "summary": classification(rows),
                    "latency_ms": distribution([r["metrics"]["elapsed_ms"] for r in rows]),
                    "cost_usd": sum(costs) if all(c is not None for c in costs) else None,
                    "by_category": {
                        c: classification([r for r in rows if r["category"] == c])
                        for c in sorted({r["category"] for r in rows})
                    },
                    "cases": rows,
                }
                args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(
                    f"{row['id']} predicted={row['predicted']} expected={row['expected']} error={row['error']}",
                    flush=True,
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
