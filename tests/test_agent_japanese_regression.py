"""Deterministic replay contracts, not claims that mocked tests exercise a live LLM."""

import json

import pytest

from backend.config import ROOT, Settings
from backend.rag import answer_from_sources
from backend.verification import AGENT_GENERATION_RULES, AGENT_VERIFICATION_RULES
from scripts.agent_verifier_replay import cases

FIXTURE = json.loads((ROOT / "evals/agent-ja-regression.json").read_text(encoding="utf-8"))


class Replay:
    def __init__(self, generated, verdicts):
        self.generated, self.verdicts, self.calls = generated, verdicts, []

    def chat(self, settings, key, messages, **options):
        self.calls.append((messages, options))
        assert settings.verification_mode == "strict" and settings.verification_strategy == "all"
        if options.get("role") == "verifier":
            assert AGENT_VERIFICATION_RULES in messages[0]["content"]
            return json.dumps({"verdicts": self.verdicts}, ensure_ascii=False)
        assert AGENT_GENERATION_RULES in messages[0]["content"]
        return json.dumps(self.generated, ensure_ascii=False)


def run(provider):
    inputs = FIXTURE["generator_input"]
    sources = [source | {"number": source["id"]} for source in inputs["sources"]]
    return answer_from_sources(
        inputs["question"],
        Settings(mode="api", verification_mode="off"),
        "test",
        sources,
        "ja",
        provider,
        agent_mode=True,
    )


def test_recorded_generator_citation_omission_remains_rejected_without_borrowing_other_claims():
    provider = Replay(FIXTURE["generator_output"], FIXTURE["verifier_output"]["verdicts"])
    response = run(provider)
    assert response["status"] == "unsupported_answer"
    assert response["support"]["verified_claims"] == 2
    assert response["claims"] == [] and response["sources"] == []
    assert "evaluation_candidate" not in response
    claims = json.loads(provider.calls[-1][0][-1]["content"])["claims"]
    assert {p["kind"] for p in claims[1]["cited_passages"]} == {"user"}
    assert json.loads(FIXTURE["generator_input"]["question"])[-1]["responding_to"]


@pytest.mark.parametrize("row", cases()[1], ids=lambda row: row["id"])
def test_japanese_modality_replay_preserves_positive_and_negative_verdicts(row):
    claim = row["claim"]
    generated = {
        "status": "answered",
        "claims": [
            {
                "text": claim["text"],
                "evidence": [{"source_id": p["source_id"], "quote": p["quote"]} for p in claim["cited_passages"]],
            }
        ],
    }
    provider = Replay(
        generated,
        [
            {
                "claim_index": 1,
                "supported": row["expected"],
                "reason": "Controlled regression verdict; live results are reported separately",
            }
        ],
    )
    result = run(provider)
    assert (result["status"] == "answered") is row["expected"]
    assert result["support"]["verification_mode"] == "strict"
    assert len(provider.calls) == 2
    if not row["expected"]:
        assert not result["claims"] and not result["sources"]
