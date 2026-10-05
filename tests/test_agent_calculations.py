"""Deterministic display references never authorize free-form policy text."""

import copy
import json
from datetime import date

import pytest

from backend.agent import AgentContext, AgentState, Observation, Turn
from backend.agent_grounding import standalone_tool_text
from backend.agent_service import evidence_sources
from backend.agent_tools import (
    CalculatorArguments,
    CalendarArguments,
    CalendarConfig,
    calculator_result,
    calendar_result,
)
from backend.config import ROOT, Settings
from backend.rag import answer_from_sources


class Model:
    def __init__(self, claims, supported=True):
        self.claims, self.supported, self.checked = claims, supported, []

    def chat(self, settings, key, messages, **kwargs):
        if kwargs.get("role") == "verifier":
            assert settings.verification_mode == "strict" and settings.verification_strategy == "all"
            self.checked = json.loads(messages[-1]["content"])["claims"]
            return json.dumps(
                {
                    "verdicts": [
                        {
                            "claim_index": c["claim_index"],
                            "supported": self.supported,
                            "reason": "Controlled contract test",
                        }
                        for c in self.checked
                    ]
                }
            )
        return json.dumps({"status": "answered", "claims": self.claims})


def sources(kind="calculator", language="en", *, unit=None, user="Calculate 3 notebooks at 1200 JPY each"):
    context = AgentContext("alice", "scope", date(2026, 10, 5), "Asia/Tokyo", language)
    if kind == "calculator":
        args = CalculatorArguments(operation="multiply", operands=["3", "1200"], result_unit=unit)
        output = calculator_result(args)
    else:
        args = CalendarArguments(operation="date_range", start_date="2026-10-05", end_date="2026-10-07")
        output = calendar_result(args, context, CalendarConfig())
    return evidence_sources(
        AgentState(
            context=context,
            turns=[Turn(text=user)],
            observations=[Observation(id="tool_1", tool=kind, arguments=args.model_dump(), status="ok", output=output)],
            selected_observation_ids=["tool_1"],
        )
    )


def run(claims, evidence, language="en", supported=True):
    model = Model(claims, supported)
    result = answer_from_sources(
        "Check the requested calculation",
        Settings(mode="api", verification_mode="off"),
        "fixture",
        evidence,
        language,
        model,
        agent_mode=True,
    )
    return result, model


@pytest.mark.parametrize("language", ["zh", "ja", "en"])
@pytest.mark.parametrize("kind", ["calculator", "calendar"])
def test_reference_is_rendered_and_cited_by_server_and_still_verified(language, kind):
    evidence = sources(kind, language)
    result, model = run([{"calculation_source_id": 1}], evidence, language)
    assert result["status"] == "answered"
    claim = result["claims"][0]
    assert claim["text"] == standalone_tool_text(evidence[0], language)
    assert claim["evidence"] == [{"source_id": 1, "quote": claim["text"]}]
    assert claim["rendering"] == "server_calculation"
    data = claim["calculation"]
    assert data["observation_id"] == "tool_1" and data["source_id"] == 1
    if kind == "calculator":
        assert data["result"]["operands"] == ["3", "1200"] and data["result"]["result"] == "3600"
    else:
        assert data["result"]["start_date"] == "2026-10-05" and data["result"]["end_date"] == "2026-10-07"
        assert data["result"]["timezone"] == "Asia/Tokyo" and data["provenance"] == "mock"
        assert "2026-10-05" in claim["text"] and "Mock" in claim["text"]
    assert model.checked[0]["text"] == claim["text"]
    assert model.checked[0]["rendering"] == "server_calculation"
    rejected, _ = run([{"calculation_source_id": 1}], evidence, language, supported=False)
    assert rejected["status"] == "unsupported_answer" and not rejected["claims"]


def test_unit_requires_numeric_input_provenance_and_fixed_citation():
    evidence = sources(unit="JPY")
    result, _ = run([{"calculation_source_id": 1}], evidence)
    claim = result["claims"][0]
    assert "3600 JPY" in claim["text"]
    assert {e["source_id"] for e in claim["evidence"]} == {1, 2}
    assert claim["calculation"]["result"]["unit_provenance"] == "planner_input"
    for unit in ("USD", "EUR"):
        result, model = run([{"calculation_source_id": 1}], sources(unit=unit))
        assert result["status"] == "invalid_model_response" and not model.checked


@pytest.mark.parametrize(
    "claim",
    [
        {"calculation_source_id": 1, "text": "Purchase is approved."},
        {"calculation_source_id": 1, "result": "5000"},
        {"calculation_source_id": 1, "result_unit": "USD"},
        {"calculation_source_id": 1, "evidence": [{"source_id": 2, "quote": "User permission"}]},
        {"calculation_source_id": 2},  # user input is not a tool capability
        {"calculation_source_id": 999},
        {"calculation_source_id": True},
        {
            "rendering": "server_calculation",
            "text": "Permission granted",
            "evidence": [{"source_id": 1, "quote": "Calculation"}],
        },
        {"type": "calculation", "text": "Permission granted", "evidence": [{"source_id": 1, "quote": "Calculation"}]},
    ],
)
def test_no_model_classification_or_override_can_bypass_policy_gate(claim):
    result, model = run([claim], sources())
    assert result["status"] == "invalid_model_response" and not model.checked and not result["claims"]


def test_arithmetic_result_is_recomputed_and_policy_tail_is_not_silently_dropped():
    evidence = sources()
    bad = copy.deepcopy(evidence)
    bad[0]["metadata"]["result"]["result"] = "9999"
    assert run([{"calculation_source_id": 1}], bad)[0]["status"] == "invalid_model_response"
    claims = [
        {"calculation_source_id": 1},
        {
            "text": "Company policy approves this purchase.",
            "evidence": [{"source_id": 1, "quote": evidence[0]["metadata"]["standalone_text"]}],
        },
    ]
    result, model = run(claims, evidence)
    assert result["status"] == "unsupported_answer" and not model.checked


@pytest.mark.parametrize(
    "case_id,index", [("purchase-multiply-en", 0), ("leave-mock-window-zh", 0), ("return-purchase-cross-en", 2)]
)
def test_frozen_false_refusals_work_with_structured_reference_without_relabeling_policy(case_id, index):
    # Original report is read only. Replace precisely the calculation claim in a
    # controlled candidate; this is a contract test, not a replayed live model.
    report = json.loads(
        (ROOT / "reports/agent-hardening/evaluation-final-quoted-live.json").read_text(encoding="utf-8")
    )
    case = next(c for c in report["cases"] if c["id"] == case_id)
    calls = report["model_calls"][case["call_start"] : case["call_end"]]
    claims = json.loads(next(c["output"] for c in calls if c["role"] == "generator"))["claims"]
    evidence = case["turns"][-1]["retrieved_sources"]
    original, _ = run(claims, evidence, case["contract"]["language"])
    assert original["status"] == "unsupported_answer"
    tool = next(
        s
        for s in evidence
        if s["kind"] == "tool" and s["number"] in {e["source_id"] for e in claims[index]["evidence"]}
    )
    tool["text"] += "\n" + standalone_tool_text(tool, case["contract"]["language"])
    claims[index] = {"calculation_source_id": tool["number"]}
    result, model = run(claims, evidence, case["contract"]["language"])
    assert result["status"] == "answered" and len(model.checked) == len(claims)
    assert result["claims"][index]["rendering"] == "server_calculation"
    assert all(
        c.get("rendering") == "server_calculation" if c["claim_index"] == index + 1 else "rendering" not in c
        for c in model.checked
    )
