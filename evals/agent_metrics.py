"""Agent metrics: planning and delivered answer quality have separate denominators."""

import statistics
from collections import Counter

from .metrics import percentile

PHASES = (
    "agent_planning",
    "agent_tool_knowledge_search",
    "agent_tool_calendar",
    "agent_tool_calculator",
    "generation",
    "verification",
)


def validate_dataset(data):
    cases = data["cases"]
    if not 20 <= len(cases) <= 30 or len({c["id"] for c in cases}) != len(cases):
        raise ValueError("Use 20-30 independently identified scenarios")
    for case in cases:
        if (
            not set(case["required_tools"])
            <= set(case["allowed_tools"])
            <= {"knowledge_search", "calculator", "calendar"}
        ):
            raise ValueError("Invalid tool contract")
        if case["requires_clarification"] != bool(case.get("reply")):
            raise ValueError("Clarification needs a scripted user reply")
        if not all(1 <= page <= len(data["pages"]) for page in case["gold_pages"]):
            raise ValueError("Invalid reference page")
        if case["answerable"] and not case["gold_pages"]:
            raise ValueError("Answerable policy tasks need reference evidence")


def score_case(case, turns, judgment):
    final = turns[-1] if turns else {}
    trace = final.get("trace", [])  # Cumulative trace; don't double-count resumed turns.
    calls = [e for e in trace if e["event"] in ("tool_completed", "tool_error")]
    used = {e["tool"] for e in calls}
    tools_ok = set(case["required_tools"]) <= used <= set(case["allowed_tools"]) and all(
        e["event"] == "tool_completed" for e in calls
    )
    clarified = any(t.get("status") == "needs_input" for t in turns)
    clarify_ok = clarified == case["requires_clarification"]
    handed_off = any(e["event"] == "ready" for e in trace)
    terminal_ok = final.get("status") in case["expected_statuses"]
    # A planner can succeed even if generation/verification later fails.
    planning = tools_ok and clarify_ok and (handed_off if case["answerable"] else terminal_ok)
    delivered = final.get("status") == "answered"
    grounded = (
        delivered
        and judgment.get("citation_groundedness") == 1
        and final.get("support", {}).get("all_supported") is True
    )
    answer_ok = delivered and judgment.get("answer_correctness") == 1 and grounded
    return {
        "planning_success": bool(planning),
        "tool_selection_accuracy": bool(tools_ok),
        "clarification_accuracy": bool(clarify_ok),
        "task_success": bool(planning and terminal_ok and (answer_ok if case["answerable"] else True)),
        "answer_correct": bool(delivered and judgment.get("answer_correctness") == 1) if case["answerable"] else None,
        "grounded_answer": bool(grounded) if case["answerable"] else None,
        "delivered": delivered,
        "tool_calls": len(calls),
        "planner_calls": sum(e["event"] in ("call_tool", "clarify", "prepare_answer", "unavailable") for e in trace),
        "duplicate_calls": sum(e.get("code") == "duplicate_call" for e in calls),
        "used_tools": sorted(used),
        "final_status": final.get("status", "error"),
    }


def task_usage(turns):
    metrics = [turn.get("metrics", {}) for turn in turns]
    costs = [m.get("cost_usd") for m in metrics]
    tokens = Counter()
    for m in metrics:
        tokens.update(
            {
                k: m.get("token_usage", {}).get(k, 0)
                for k in ("input_tokens", "output_tokens", "embedding_tokens", "total_tokens")
            }
        )
    return {
        "elapsed_ms": sum(m.get("elapsed_ms", 0) for m in metrics),
        "cost_usd": sum(costs) if costs and all(c is not None for c in costs) else None,
        "token_usage": dict(tokens),
        "timings_ms": {phase: sum(m.get("timings_ms", {}).get(phase, 0) for m in metrics) for phase in PHASES},
    }


def distribution(values):
    return {
        "count": len(values),
        "mean": statistics.mean(values) if values else None,
        "p50": percentile(values, 50),
        "p95": percentile(values, 95),
    }


def summarize(rows, expected):
    scores = [row["scores"] for row in rows]
    usage = [row["usage"] for row in rows]
    costs = [u["cost_usd"] for u in usage]
    quality = [s for s in scores if s["answer_correct"] is not None]
    delivered = [s for s in quality if s["delivered"]]

    def mean(values):
        return statistics.mean(values) if values else None

    return {
        "completed": len(rows),
        "expected": expected,
        "complete": len(rows) == expected,
        **{
            key: mean([s[key] for s in scores])
            for key in ("task_success", "planning_success", "tool_selection_accuracy", "clarification_accuracy")
        },
        "answer_correctness": mean([s["answer_correct"] for s in quality]),
        "grounded_answer_rate": mean([s["grounded_answer"] for s in quality]),
        "grounded_rate_among_delivered": mean([s["grounded_answer"] for s in delivered]),
        "answerable_tasks": len(quality),
        "delivered_answers": len(delivered),
        "tool_calls": sum(s["tool_calls"] for s in scores),
        "tool_calls_per_task": mean([s["tool_calls"] for s in scores]),
        "planner_calls_per_task": mean([s["planner_calls"] for s in scores]),
        "duplicate_calls": sum(s["duplicate_calls"] for s in scores),
        "latency_ms": distribution([u["elapsed_ms"] for u in usage]),
        "phase_latency_ms": {phase: distribution([u["timings_ms"][phase] for u in usage]) for phase in PHASES},
        "cost_per_task_usd": mean(costs) if costs and all(c is not None for c in costs) else None,
        "known_cost_usd": sum(c for c in costs if c is not None),
        "unknown_cost_tasks": sum(c is None for c in costs),
        "token_usage": dict(sum((Counter(u["token_usage"]) for u in usage), Counter())),
        "statuses": dict(Counter(s["final_status"] for s in scores)),
    }


def markdown(report):
    s = report["summary"]
    text = f"# Agent Evaluation: {report['label']}\n\n{report['scope']}\n\nDataset: `{report['dataset_sha256']}`. Completed {s['completed']}/{s['expected']}.\n\n"
    text += "Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.\n\n"
    text += "| Metric | Value |\n| --- | --- |\n"
    for key in (
        "task_success",
        "planning_success",
        "tool_selection_accuracy",
        "clarification_accuracy",
        "answer_correctness",
        "grounded_answer_rate",
        "grounded_rate_among_delivered",
        "tool_calls_per_task",
        "planner_calls_per_task",
        "cost_per_task_usd",
    ):
        text += f"| {key} | {s[key]} |\n"
    text += f"\nTask latency ms: `{s['latency_ms']}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.\n\n| Phase | P50 ms | P95 ms |\n| --- | --- | --- |\n"
    for phase, values in s["phase_latency_ms"].items():
        text += f"| {phase} | {values['p50']} | {values['p95']} |\n"
    text += "\nPhase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.\n\n| Scenario | Status | Planning | Task success | Calls | ms | USD |\n| --- | --- | --- | --- | --- | --- | --- |\n"
    for row in report["cases"]:
        a, u = row["scores"], row["usage"]
        text += f"| {row['id']} | {a['final_status']} | {a['planning_success']} | {a['task_success']} | {a['tool_calls']} | {u['elapsed_ms']:.0f} | {u['cost_usd']} |\n"
    return text
