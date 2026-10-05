"""Validate explicit human annotations; pending samples never count as reviewed."""

import argparse
import json
from datetime import datetime
from pathlib import Path

from backend.config import ROOT
from scripts.prepare_agent_review import fingerprint


def summarize(data, annotations):
    if annotations.get("dataset_sha256") != fingerprint(data):
        raise ValueError("Review does not match the frozen dataset")
    rows = annotations.get("cases", [])
    expected = {c["id"] for c in data["cases"]}
    if len(rows) != len(expected) or {r["id"] for r in rows} != expected:
        raise ValueError("Every case must appear exactly once")
    complete = [
        r
        for r in rows
        if all(type(r.get(k)) is bool for k in ("answer_correct", "all_claims_supported", "reference_approved"))
    ]
    signed = annotations.get("human_attested") is True and bool(str(annotations.get("reviewer") or "").strip())
    timestamp = annotations.get("reviewed_at")
    if signed:
        if not timestamp or datetime.fromisoformat(timestamp).tzinfo is None:
            raise ValueError("Signed review requires a timezone-aware timestamp")
    reviewed = len(complete) if signed else 0
    status = "reviewed" if reviewed == len(expected) else "pending_human_review"
    if status == "reviewed" and not all(r["reference_approved"] for r in rows):
        status = "needs_adjudication"
    recorded = next((r for r in complete if r["id"] == "H01"), None) if signed else None
    return {
        "dataset_sha256": fingerprint(data),
        "status": status,
        "human_reviewed": reviewed,
        "total": len(expected),
        "reviewer": annotations.get("reviewer") if signed else None,
        "reviewed_at": timestamp if signed else None,
        "candidate_correctness": sum(r["answer_correct"] for r in complete) / reviewed
        if status == "reviewed"
        else None,
        "candidate_groundedness": sum(r["all_claims_supported"] for r in complete) / reviewed
        if status == "reviewed"
        else None,
        "scope": "Accuracy of this mix of frozen/constructed candidates, not live Agent task success. Human identity is attested by the reviewer, not verified by this script.",
        "frozen_verifier_agrees_on_H01": recorded["all_claims_supported"] == data["frozen_failure"]["runtime_supported"]
        if recorded
        else None,
        "annotations": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise SystemExit("Preserve earlier reviews; choose a new report path")
    data = json.loads((ROOT / "evals/agent-human-review-v1.json").read_text(encoding="utf-8"))
    report = summarize(data, json.loads(Path(args.annotations).read_text(encoding="utf-8")))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(
        f"# Human review status\n\nStatus: **{report['status']}**. Human-reviewed: {report['human_reviewed']}/{report['total']}.\n\nPending or unapproved references never produce an accuracy claim. See the JSON for the frozen dataset hash and annotations.\n",
        encoding="utf-8",
    )
    print(report["status"], f"{report['human_reviewed']}/{report['total']}")


if __name__ == "__main__":
    main()
