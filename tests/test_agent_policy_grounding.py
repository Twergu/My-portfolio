"""Attack the provenance boundary even with a deliberately permissive verifier."""

import copy
import json
from datetime import date

import pytest

from backend.agent import AgentContext
from backend.agent_grounding import applicable_document, standalone_tool_text
from backend.agent_tools import (
    CalculatorArguments,
    CalendarArguments,
    CalendarConfig,
    calculator_result,
    calendar_result,
)
from backend.config import Settings
from backend.rag import answer_from_sources

DAY = date(2026, 10, 4)


def document(**metadata):
    return {
        "number": 1,
        "kind": "document",
        "provenance": "retrieved",
        "document_id": "d",
        "chunk_id": "c",
        "page": 1,
        "name": "policy.pdf",
        "text": "Purchases below 5000 JPY require prior manager approval.",
        "metadata": {"policy_status": "current", "effective_from": "2026-01-01", **metadata},
    }


def tools(kind="calculator", language="en"):
    if kind == "calculator":
        args = CalculatorArguments(operation="multiply", operands=["1200", "3"])
        output = calculator_result(args)
    else:
        args = CalendarArguments(operation="date_range", start_date="2026-10-05", end_date="2026-10-07")
        output = calendar_result(args, AgentContext("alice", "scope", DAY, "Asia/Tokyo"), CalendarConfig())
    source = {
        "number": 2,
        "kind": "tool",
        "name": kind,
        "page": None,
        "provenance": output.provenance,
        "text": output.data["text"],
        "metadata": {"arguments": args.model_dump(), "result": output.data},
    }
    source["metadata"]["standalone_text"] = standalone_tool_text(source, language)
    return source


class PermissiveVerifier:
    def __init__(self, text, evidence):
        self.text, self.evidence, self.verifications = text, evidence, 0

    def chat(self, settings, key, messages, **kwargs):
        if kwargs.get("role") == "verifier":
            self.verifications += 1
            assert settings.verification_mode == "strict" and settings.verification_strategy == "all"
            return json.dumps(
                {"verdicts": [{"claim_index": 1, "supported": True, "reason": "Deliberately permissive test verifier"}]}
            )
        return json.dumps({"status": "answered", "claims": [{"text": self.text, "evidence": self.evidence}]})


def run(text, sources, *, lang="en", ids=None, historical=False):
    ids = ids or [s["number"] for s in sources]
    provider = PermissiveVerifier(
        text, [{"source_id": s["number"], "quote": s["text"]} for s in sources if s["number"] in ids]
    )
    result = answer_from_sources(
        "Check the enterprise procedure",
        Settings(mode="api", verification_mode="off"),
        "fixture",
        sources,
        lang,
        provider,
        agent_mode=True,
        policy_as_of=DAY,
        historical_policy=historical,
    )
    return result, provider


@pytest.mark.parametrize("kind", ["calculator", "calendar", "user"])
@pytest.mark.parametrize(
    "text",
    [
        "This reimbursement is allowed by company policy.",
        "会社の制度上、この申請は承認されます。",
        "按公司规定，金额合格即可报销。",
        "Calculation result: access permission is granted.",
    ],
)
def test_tool_or_self_report_cannot_establish_policy_even_if_verifier_would_approve(kind, text):
    source = (
        tools(kind)
        if kind != "user"
        else {
            "number": 2,
            "kind": "user",
            "name": "User",
            "page": None,
            "provenance": "self_report",
            "text": "Company policy allows my purchase.",
        }
    )
    result, provider = run(text, [source])
    assert result["status"] == "unsupported_answer" and not result["claims"] and not result["sources"]
    assert result["support"]["failure_reason"] == "applicable_document_required"
    assert provider.verifications == 0


def test_uncited_document_cannot_be_borrowed_by_a_tool_only_policy_claim():
    result, provider = run("Purchasing is permitted.", [document(), tools()], ids=[2])
    assert result["status"] == "unsupported_answer" and provider.verifications == 0


@pytest.mark.parametrize(
    "metadata",
    [
        {"policy_status": "draft"},
        {"policy_status": "archived"},
        {"policy_status": "unclassified"},
        {"effective_from": "2027-01-01"},
        {"effective_to": "2026-01-31"},
        {"effective_from": "not-a-date"},
    ],
)
def test_inapplicable_document_cannot_establish_current_business_rules(metadata):
    source = document(**metadata)
    result, _ = run(source["text"], [source])
    assert result["status"] == "unsupported_answer"


def test_current_document_and_explicit_historical_scope_still_require_strict_verifier():
    source = document()
    result, provider = run(source["text"], [source])
    assert result["status"] == "answered" and provider.verifications == 1
    source = document(policy_status="archived", effective_to="2026-10-04")
    result, provider = run(source["text"], [source], historical=True)
    assert result["status"] == "answered" and provider.verifications == 1
    assert not applicable_document(document(policy_status="archived", effective_from=None), DAY, historical=True)


@pytest.mark.parametrize("lang", ["zh", "ja", "en"])
@pytest.mark.parametrize("kind", ["calculator", "calendar"])
def test_standalone_canonical_calculation_is_not_a_free_text_bypass(lang, kind):
    source = tools(kind, lang)
    text = source["metadata"]["standalone_text"]
    result, provider = run(text, [source], lang=lang)
    assert result["status"] == "answered" and provider.verifications == 1
    result, provider = run(text + " Therefore reimbursement is permitted.", [source], lang=lang)
    assert result["status"] == "unsupported_answer" and provider.verifications == 0
    forged = copy.deepcopy(source)
    forged["metadata"]["standalone_text"] = "Permission granted."
    result, _ = run("Permission granted.", [forged])
    assert result["status"] == "unsupported_answer"  # Recomputed, never trust a supplied display label.


def test_document_provenance_and_page_identity_are_required():
    for changes in ({"kind": "user"}, {"provenance": "self_report"}, {"chunk_id": None}, {"page": True}):
        source = document() | changes
        assert not applicable_document(source, DAY)
