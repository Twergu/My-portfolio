"""Scoring contracts use fixed records, never pretend to be live API evaluation."""

import copy
import json

import pytest

from backend.config import ROOT
from evals.agent_metrics import PHASES, markdown, score_case, summarize, task_usage, validate_dataset
from evals.make_agent import dataset
from scripts.agent_compare import compare


def test_agent_dataset_is_reproducible_diverse_and_preserves_japanese_failure_scenario():
    data = json.loads((ROOT / "evals/agent_dataset.json").read_text(encoding="utf-8"))
    assert data == dataset()
    validate_dataset(data)
    assert len(data["cases"]) == 24
    assert {c["language"] for c in data["cases"]} == {"zh", "ja", "en"}
    assert {tag for c in data["cases"] for tag in c["tags"]} == {
        "knowledge",
        "clarification",
        "multi_step",
        "unavailable",
    }
    ja = next(c for c in data["cases"] if c["id"] == "commuter-clarify-ja")
    assert ja["requires_clarification"] and "提出できます" in ja["reply"]


@pytest.mark.parametrize("mutation", ["duplicate", "invalid_tool", "missing_reply", "gold"])
def test_bad_eval_contract_fails_before_paid_calls(mutation):
    data = dataset()
    if mutation == "duplicate":
        data["cases"][1]["id"] = data["cases"][0]["id"]
    elif mutation == "invalid_tool":
        data["cases"][0]["required_tools"] = ["send_email"]
    elif mutation == "missing_reply":
        data["cases"][0]["requires_clarification"] = True
    else:
        data["cases"][0]["gold_pages"] = [99]
    with pytest.raises(ValueError):
        validate_dataset(data)


def answer_record():
    return {
        "status": "answered",
        "trace": [
            {"event": "call_tool"},
            {"event": "tool_completed", "tool": "knowledge_search"},
            {"event": "prepare_answer"},
            {"event": "ready"},
        ],
        "support": {"all_supported": True},
    }


def test_planning_and_answer_are_separate_and_failure_is_in_denominator():
    case = dataset()["cases"][0]
    good = answer_record()
    s = score_case(case, [good], {"answer_correctness": 1, "citation_groundedness": 1})
    assert s["task_success"] and s["planning_success"]
    failed = copy.deepcopy(good)
    failed.update(status="unsupported_answer", support={})
    bad = score_case(case, [failed], {})
    assert bad["planning_success"] and not bad["task_success"] and not bad["grounded_answer"]
    usage = task_usage([{"metrics": {"elapsed_ms": 100, "cost_usd": 0.01}}])
    rows = [{"id": "good", "scores": s, "usage": usage}, {"id": "bad", "scores": bad, "usage": usage}]
    summary = summarize(rows, 24)
    assert summary["task_success"] == summary["grounded_answer_rate"] == 0.5
    assert summary["grounded_rate_among_delivered"] == 1
    assert not summary["complete"] and summary["planning_success"] == 1
    assert "bad" in markdown(
        {"label": "test", "scope": "Controlled records", "dataset_sha256": "abc", "cases": rows, "summary": summary}
    )


def test_unavailable_is_not_safety_error_or_fabricated_answer():
    case = next(c for c in dataset()["cases"] if c["id"] == "unavailable-ticket-en")
    assert score_case(case, [{"status": "unavailable"}], {})["task_success"]
    for status in ("unsupported_answer", "error", "answered", "needs_input"):
        assert not score_case(case, [{"status": status}], {})["task_success"]


def test_resume_trace_not_double_counted_and_unexpected_tool_is_failure():
    case = dataset()["cases"][0]
    first = answer_record() | {"status": "needs_input"}
    final = answer_record()
    score = score_case(case, [first, final], {"answer_correctness": 1, "citation_groundedness": 1})
    assert score["tool_calls"] == 1 and score["planner_calls"] == 2
    assert not score["clarification_accuracy"] and not score["task_success"]
    final["trace"].append({"event": "tool_error", "tool": "calendar", "code": "duplicate_call"})
    score = score_case(case, [final], {})
    assert not score["tool_selection_accuracy"] and score["duplicate_calls"] == 1


def test_usage_excludes_judge_and_thinking_time_unknown_cost_not_zero():
    turns = [
        {
            "metrics": {
                "elapsed_ms": 40,
                "cost_usd": 0.01,
                "token_usage": {"total_tokens": 100, "complete": True},
                "timings_ms": {"agent_planning": 20},
            }
        },
        {
            "metrics": {
                "elapsed_ms": 60,
                "cost_usd": None,
                "token_usage": {"total_tokens": 50},
                "timings_ms": {"generation": 20, "verification": 30},
            }
        },
    ]
    usage = task_usage(turns)
    assert usage["elapsed_ms"] == 100 and usage["cost_usd"] is None
    assert usage["token_usage"]["total_tokens"] == 150 and "complete" not in usage["token_usage"]
    assert set(usage["timings_ms"]) == set(PHASES)
    assert usage["timings_ms"]["verification"] == 30


def test_comparison_keeps_failures_and_refuses_mismatched_or_partial_runs():
    case = dataset()["cases"][0]
    score = score_case(case, [answer_record()], {"answer_correctness": 1, "citation_groundedness": 1})
    usage = task_usage([{"metrics": {"elapsed_ms": 100, "cost_usd": 0.01}}])
    row = {"id": "same", "scores": score, "usage": usage}
    before = {
        "dataset_sha256": "frozen",
        "source_sha256": "before",
        "settings": {},
        "cases": [row],
        "summary": summarize([row], 1),
    }
    after = copy.deepcopy(before)
    after["cases"][0]["scores"].update(task_success=False, final_status="unsupported_answer", delivered=False)
    after["summary"] = summarize(after["cases"], 1)
    result = compare(before, after)
    assert len(result["paired"]) == 1 and not result["paired"][0]["after_success"]
    assert result["both_successful_answered_cohort"]["ids"] == []
    after["summary"]["complete"] = False
    with pytest.raises(ValueError, match="incomplete"):
        compare(before, after)
    after["dataset_sha256"] = "changed"
    with pytest.raises(ValueError, match="Dataset"):
        compare(before, after)
