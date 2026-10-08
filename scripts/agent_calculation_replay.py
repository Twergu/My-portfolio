"""Replay a frozen calculation false rejection through the real Strict Verifier."""

import argparse
import copy
import json
import os
from pathlib import Path

from backend.agent_grounding import render_calculation
from backend.config import ROOT, environment_settings
from backend.telemetry import Metrics
from backend.verification import verify_claims
from scripts.agent_diagnose import RecordingProvider


def run(output):
    output = Path(output)
    if output.exists():
        raise SystemExit("Preserve prior replay results")
    original = "reports/agent-followup/five-cases-final-live.json"
    saved = json.loads((ROOT / original).read_text(encoding="utf-8"))
    case = next(c for c in saved["cases"] if c["id"] == "return-purchase-cross-en")
    calls = saved["model_calls"][case["call_start"] : case["call_end"]]
    request = json.loads(next(c for c in calls if c["role"] == "verifier")["messages"][-1]["content"])
    candidate = json.loads(next(c for c in calls if c["role"] == "generator")["output"])
    sources = case["turns"][-1]["retrieved_sources"]
    for reference, claim in zip(candidate["claims"], request["claims"], strict=True):
        if "calculation_source_id" in reference:
            source = next(s for s in sources if s["number"] == reference["calculation_source_id"])
            rendered, _ = render_calculation(source, sources, "en")
            assert claim["text"] == rendered["text"]
            claim["rendering"] = "server_calculation"
    negative = copy.deepcopy(request["claims"][0])
    negative["text"] = (
        "The RET-26 company policy guarantees that the official return deadline is 2026-10-16 and this employee has complied."
    )
    negative.pop("rendering")
    rows = [
        ("frozen_candidate_server_markers", request["claims"], [True] * len(request["claims"])),
        ("policy_inference_from_tool_only", [negative], [False]),
    ]
    settings = environment_settings().model_copy(
        update={"mode": "api", "verification_mode": "strict", "verification_strategy": "all"}
    )
    key = os.getenv("RAG_API_KEY")
    if not key:
        raise SystemExit("Configure RAG_API_KEY")
    provider = RecordingProvider()
    report = {
        "scope": "Real Strict Verifier replay, NOT a new end-to-end Agent run. Positive inputs are the preserved failed candidate with backend-validated rendering markers; the negative policy-claim control is constructed and labeled. Original failure unchanged.",
        "original": original,
        "case_id": case["id"],
        "cases": [],
        "model_calls": provider.records,
    }
    try:
        for name, claims, expected in rows:
            metrics = Metrics()
            row = {"id": name, "expected": expected}
            try:
                verdicts = verify_claims(
                    request["question"], claims, settings, key, provider, metrics, prompt="baseline", agent_mode=True
                )
                row.update(
                    verdicts=[v.model_dump() for v in verdicts],
                    matches_expected=[v.supported for v in verdicts] == expected,
                )
            except Exception as exc:
                row.update(error_type=type(exc).__name__, matches_expected=False)
            row["usage"] = metrics.as_dict()
            report["cases"].append(row)
            print(name, row["matches_expected"], flush=True)
    finally:
        provider.close()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if not args.live:
        parser.error("--live permits paid calls on the frozen fictional case")
    run(args.output)
