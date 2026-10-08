"""Replay the captured Japanese failure against the real strict verifier, with negative controls."""

import argparse
import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from backend.config import ROOT, environment_settings
from backend.telemetry import Metrics
from backend.verification import verify_claims
from scripts.agent_diagnose import RecordingProvider


def cases():
    fixture = json.loads((ROOT / "evals/agent-ja-regression.json").read_text(encoding="utf-8"))
    claims = fixture["verifier_input"]["claims"]
    rows = [
        {"id": "missing_document", "claim": copy.deepcopy(claims[1]), "expected": False},
        {"id": "normative_submission", "claim": copy.deepcopy(claims[2]), "expected": True},
        {"id": "explicit_requirement", "claim": copy.deepcopy(claims[2]), "expected": True},
        {"id": "completed_submission", "claim": copy.deepcopy(claims[2]), "expected": False},
        {"id": "conditional_assessment", "claim": copy.deepcopy(claims[1]), "expected": True},
        {"id": "wrong_onsite_days", "claim": copy.deepcopy(claims[1]), "expected": False},
    ]
    rows[2]["claim"]["text"] = "申請には雇用形態申告書と出社勤務スケジュールの提出が必要です。"
    rows[3]["claim"]["text"] = "あなたは雇用形態申告書と出社勤務スケジュールを提出済みです。"
    rows[4]["claim"]["text"] = (
        "自己申告に基づけばフルタイム勤務・週3日出社という規定の条件に該当しますが、雇用主の確認が必要です。"
    )
    rows[4]["claim"]["cited_passages"].extend(copy.deepcopy(claims[0]["cited_passages"]))
    rows[5]["claim"]["text"] = "自己申告によれば週2日出社であり、通勤補助の条件に該当します。"
    rows[5]["claim"]["cited_passages"].extend(copy.deepcopy(claims[0]["cited_passages"]))
    for index, row in enumerate(rows, 1):
        row["claim"]["claim_index"] = index
    return fixture["verifier_input"]["question"], rows


def run(output):
    question, rows = cases()
    settings = environment_settings().model_copy(update={"verification_mode": "strict", "verification_strategy": "all"})
    if not os.getenv("RAG_API_KEY"):
        raise SystemExit("API key missing")
    metrics = Metrics()
    with RecordingProvider() as provider:
        verdicts = verify_claims(
            question,
            [r["claim"] for r in rows],
            settings,
            os.environ["RAG_API_KEY"],
            provider,
            metrics,
            prompt="baseline",
            agent_mode=True,
        )
        result = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scope": "Real verifier replay; recorded claims plus explicitly authored controls, not end-to-end generation",
            "cases": [
                row | {"verdict": verdict.model_dump(), "passed": row["expected"] == verdict.supported}
                for row, verdict in zip(rows, sorted(verdicts, key=lambda v: v.claim_index), strict=True)
            ],
            "model_calls": provider.records,
            "metrics": metrics.as_dict(),
        }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print([(r["id"], r["passed"]) for r in result["cases"]])
    return 0 if all(r["passed"] for r in result["cases"]) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", default="reports/agent-hardening/p0-verifier-replay.json")
    args = parser.parse_args()
    if not args.live:
        parser.error("--live required for paid API calls")
    raise SystemExit(run(args.output))
