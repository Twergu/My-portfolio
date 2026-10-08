"""Compare immutable same-dataset real Agent runs; no filtering failed tasks."""

import argparse
import json
from pathlib import Path

from evals.agent_metrics import distribution


def compare(before, after):
    if before["dataset_sha256"] != after["dataset_sha256"] or before["settings"] != after["settings"]:
        raise ValueError("Dataset and model/search/verification settings must match")
    if not before["summary"]["complete"] or not after["summary"]["complete"]:
        raise ValueError("Do not compare incomplete runs as full evaluations")
    old, new = ({r["id"]: r for r in report["cases"]} for report in (before, after))
    if set(old) != set(new):
        raise ValueError("Scenario identities must match")
    result = {
        "scope": "Two independent real API passes on the same fictional regression set. No causal/significance claim; model generation and service latency vary. All failed cases retained. Runtime Strict/all and ACL unchanged.",
        "dataset_sha256": before["dataset_sha256"],
        "source_sha256": [before["source_sha256"], after["source_sha256"]],
        "all_tasks": {"before": before["summary"], "after": after["summary"]},
        "paired": [],
    }
    for id in old:
        a, b = old[id], new[id]
        result["paired"].append(
            {
                "id": id,
                "before_status": a["scores"]["final_status"],
                "after_status": b["scores"]["final_status"],
                "before_success": a["scores"]["task_success"],
                "after_success": b["scores"]["task_success"],
                "latency_delta_ms": b["usage"]["elapsed_ms"] - a["usage"]["elapsed_ms"],
                "planner_call_delta": b["scores"]["planner_calls"] - a["scores"]["planner_calls"],
            }
        )
    # Supplement all-task results with the same successful tasks in both runs.
    # This cohort is selected retrospectively, so it is not the headline score.
    both = [
        id
        for id in old
        if old[id]["scores"]["task_success"]
        and new[id]["scores"]["task_success"]
        and old[id]["scores"]["delivered"]
        and new[id]["scores"]["delivered"]
    ]
    result["both_successful_answered_cohort"] = {
        "ids": both,
        "before_ms": distribution([old[id]["usage"]["elapsed_ms"] for id in both]),
        "after_ms": distribution([new[id]["usage"]["elapsed_ms"] for id in both]),
    }
    return result


def render(data):
    text = (
        "# Agent latency / cost comparison\n\n"
        + data["scope"]
        + "\n\n| Metric | Before | After |\n| --- | --- | --- |\n"
    )
    a, b = data["all_tasks"]["before"], data["all_tasks"]["after"]
    for name in (
        "task_success",
        "planning_success",
        "tool_selection_accuracy",
        "clarification_accuracy",
        "grounded_answer_rate",
        "planner_calls_per_task",
        "tool_calls_per_task",
        "duplicate_calls",
        "cost_per_task_usd",
    ):
        text += f"| {name} | {a[name]} | {b[name]} |\n"
    for p in ("p50", "p95"):
        text += f"| latency_ms.{p} | {a['latency_ms'][p]} | {b['latency_ms'][p]} |\n"
    text += "\n| Phase | Before P50/P95 ms | After P50/P95 ms |\n| --- | --- | --- |\n"
    for phase, va in a["phase_latency_ms"].items():
        vb = b["phase_latency_ms"][phase]
        text += f"| {phase} | {va['p50']:.1f} / {va['p95']:.1f} | {vb['p50']:.1f} / {vb['p95']:.1f} |\n"
    text += (
        "\nDifferent refusal/delivery mixes affect whole-set latency. Supplementary same-successful-answer cohort (selected after runs, not a replacement score):\n\n```json\n"
        + json.dumps(data["both_successful_answered_cohort"], indent=2)
        + "\n```\n"
    )
    return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = compare(
        json.loads(Path(args.before).read_text(encoding="utf-8")),
        json.loads(Path(args.after).read_text(encoding="utf-8")),
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(render(result), encoding="utf-8")
