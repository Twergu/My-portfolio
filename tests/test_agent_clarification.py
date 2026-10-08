"""Question/reply contracts from frozen failures; semantic quality is tested live."""

import json

import pytest
from test_agent_integration import action, ready, search
from test_agent_integration import api as api

from backend.agent import Turn
from backend.clarification import clarification_context
from backend.config import ROOT, Settings
from backend.rag import answer_from_sources


def frozen_case(id):
    report = json.loads(
        (ROOT / "reports/agent-hardening/evaluation-final-quoted-live.json").read_text(encoding="utf-8")
    )
    return next(c for c in report["cases"] if c["id"] == id)


@pytest.mark.parametrize("id", ["commuter-clarify-ja", "training-clarify-ja"])
def test_frozen_resume_keeps_original_outcome_and_every_answer_for_planner_and_generator(api, id):
    client, app, models, _ = api
    case = frozen_case(id)
    assert case["turns"][-1]["status"] == "needs_input"  # Do not rewrite the recorded failure.
    contract, questions = case["contract"], case["turns"][0]["questions"]
    models.decisions = [search(), action("clarify", questions=questions), ready("tool_1")]
    first = client.post("/api/agent", json={"question": contract["question"], "language": "ja"}).json()
    result = client.post(f"/api/agent/{first['task_id']}/reply", json={"question": contract["reply"]}).json()
    assert result["status"] == "answered"
    planner = [json.loads(m[-1]["content"]) for role, m in models.calls if role == "planner"][-1]
    generator = next(json.loads(m[-1]["content"]) for role, m in models.calls if role == "generator")
    context = planner["clarification_context"]
    assert generator["clarification_context"] == context
    assert generator["policy_scope"]["as_of"] == first["reference_date"]
    assert generator["policy_scope"]["historical"] is False
    assert context["requested_outcome"] == contract["question"]
    assert context["statements"][1] == {
        "turn": 2,
        "text": contract["reply"],
        "responding_to": questions,
        "provenance": "self_report",
    }
    assert not app.state.agent.tasks


def test_partial_or_conflicting_reply_is_not_automatically_marked_complete():
    context = clarification_context(
        [
            Turn(text="Calculate the TOTAL for all courses"),
            Turn(text="Each costs 20000 JPY", responding_to=["What is the fee and how many courses?"]),
            Turn(text="Correction: each costs 25000 JPY", responding_to=["How many courses?"]),
        ]
    )
    assert context["requested_outcome"] == "Calculate the TOTAL for all courses"
    assert [s["text"] for s in context["statements"]][1:] == [
        "Each costs 20000 JPY",
        "Correction: each costs 25000 JPY",
    ]
    assert all(
        s["provenance"] == "self_report" and "verified" not in s and "complete" not in s for s in context["statements"]
    )


def test_genuinely_missing_aggregate_count_still_allows_focused_followup(api):
    client, app, models, _ = api
    models.decisions = [
        search(),
        action("clarify", questions=["Fee per course and total number of courses?"]),
        action("clarify", questions=["How many courses are included in the total?"]),
    ]
    first = client.post(
        "/api/agent", json={"question": "Calculate the total reimbursement for all courses", "language": "en"}
    ).json()
    result = client.post(f"/api/agent/{first['task_id']}/reply", json={"question": "Each costs 20000 JPY"}).json()
    assert result["status"] == "needs_input" and result["questions"] == ["How many courses are included in the total?"]
    assert not any(role in ("generator", "verifier") for role, _ in models.calls)
    client.delete(f"/api/agent/{result['task_id']}")
    assert not app.state.agent.tasks


@pytest.mark.parametrize("repair_succeeds,verifier_supports", [(True, True), (True, False), (False, True)])
def test_mixed_answer_and_questions_get_one_schema_repair_then_full_strict_verification(
    repair_succeeds, verifier_supports
):
    text = "Applicants need employer confirmation."
    source = {
        "number": 1,
        "name": "policy.pdf",
        "page": 1,
        "document_id": "doc",
        "chunk_id": "chunk",
        "kind": "document",
        "provenance": "retrieved",
        "metadata": {"policy_status": "current"},
        "text": text,
    }
    candidate = {
        "status": "answered",
        "claims": [{"text": text, "evidence": [{"source_id": 1, "quote": text}]}],
        "questions": ["Are you full-time?"],
    }

    class Model:
        generated = 0
        verified = 0

        def chat(self, settings, key, messages, **kwargs):
            assert settings.verification_mode == "strict" and settings.verification_strategy == "all"
            if kwargs.get("role") == "verifier":
                self.verified += 1
                return json.dumps(
                    {"verdicts": [{"claim_index": 1, "supported": verifier_supports, "reason": "Controlled test"}]}
                )
            self.generated += 1
            if self.generated == 2 and repair_succeeds:
                return json.dumps(candidate | {"questions": []})
            return json.dumps(candidate)

    model = Model()
    result = answer_from_sources(
        "Explain application conditions", Settings(mode="api"), "fixture", [source], "en", model, agent_mode=True
    )
    assert model.generated == 2 and model.verified == int(repair_succeeds)
    assert result["metrics"]["validation_failures"] == [
        {"role": "generator", "code": "invalid_schema", "repair_attempted": True}
    ]
    assert result["status"] == (
        "answered"
        if repair_succeeds and verifier_supports
        else "unsupported_answer"
        if repair_succeeds
        else "invalid_model_response"
    )
    if result["status"] != "answered":
        assert not result["claims"] and not result["sources"]
