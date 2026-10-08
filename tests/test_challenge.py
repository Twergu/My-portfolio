import json

import httpx
import pytest

from backend.config import Settings, environment_database_url
from backend.providers import ModelError, OpenAICompatibleProvider
from backend.telemetry import Metrics
from evals.judge import judge_answer
from evals.metrics import answer_metrics, retrieval_at_cutoffs
from scripts.evaluate import HARD_DATASET, load_dataset
from scripts.init_database_password import initialize


def test_challenge_contains_competing_policies_and_cross_document_truth():
    data = load_dataset(HARD_DATASET)
    assert len(data["queries"]) > 100 and len(data["documents"]) > 30
    assert {
        "old_version",
        "current_version",
        "draft_trap",
        "similar_document",
        "numeric_trap",
        "negation",
        "exception",
        "exception_denied",
        "cross_document",
        "negative",
        "adversarial",
    } <= {q["category"] for q in data["queries"]}
    scopes = {doc["id"]: doc for doc in data["documents"]}
    for q in data["queries"]:
        assert len(q["document_ids"]) > 8
        for evidence in q["reference_evidence"]:
            assert evidence["quote"] in scopes[evidence["document_id"]]["pages"][evidence["page"] - 1]["text"]
        if q["category"] == "cross_document":
            assert len({r["document_id"] for r in q["relevance"]}) > 1
    assert {r["document_id"] for q in data["queries"] if q["split"] == "dev" for r in q["relevance"]}.isdisjoint(
        {r["document_id"] for q in data["queries"] if q["split"] == "test" for r in q["relevance"]}
    )


def test_cutoffs_do_not_read_beyond_chunk_budget():
    def row(page):
        return {"document_id": "a", "page": page}

    metrics = retrieval_at_cutoffs([row(1), row(1), row(2), row(3)], [row(3) | {"grade": 2}])
    assert metrics["recall_at_1"] == metrics["recall_at_3"] == 0
    assert metrics["recall_at_5"] == 1


def test_fast_mode_has_unknown_runtime_groundedness():
    query = {"answerable": True, "expected_facts": [], "reference_answer": "allowed"}
    result = {
        "mode": "api",
        "status": "answered",
        "claims": [{"supported": None}],
        "support": {"total_claims": 1, "verified_claims": None},
    }
    assert answer_metrics(result, query)["claim_groundedness"] is None


@pytest.mark.parametrize(
    "error", [{"code": "insufficient_quota"}, {"code": "credit_balance_exhausted", "type": "insufficient_quota"}]
)
def test_no_retry_for_exhausted_credit(error):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(429, json={"error": error})

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        provider = OpenAICompatibleProvider(client)
        with pytest.raises(ModelError) as failure:
            provider.embed(["test"], Settings(), "fixture")
    assert failure.value.code == "insufficient_quota" and len(requests) == 1


def test_independent_judge_does_not_inherit_runtime_verified_flag():
    data = load_dataset(HARD_DATASET)
    q = data["queries"][0]
    result = {
        "status": "answered",
        "answer": "The cap is 999999 yen.",
        "claims": [
            {
                "text": "The cap is 999999 yen.",
                "supported": True,
                "evidence": [{"source_id": 1, "quote": "cap is 14500 yen"}],
            }
        ],
        "sources": [{"number": 1, "text": "The cap is 14500 yen."}],
    }

    def handler(request):
        payload = json.loads(request.content)
        assert payload["model"] == "independent-judge"
        assert '"supported": true' not in payload["messages"][1]["content"]
        body = json.loads(payload["messages"][1]["content"])
        if "gold_evidence" in body:
            assert "claims" not in body
            response = {"answer_correct": False, "reason": "Wrong number"}
        else:
            assert "reference_answer" not in body and "answerable" not in body
            assert set(body) == {"question", "claims"}
            response = {"citations": [{"claim_index": 1, "supported": False, "reason": "Contradiction"}]}
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(response)}}]})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        judged = judge_answer(
            result, q, data, Settings(), "fixture", OpenAICompatibleProvider(client), "independent-judge", Metrics({})
        )
    assert judged["answer_correctness"] == judged["citation_groundedness"] == 0


@pytest.mark.parametrize("recover", [True, False])
def test_judge_format_retry_is_bounded_and_keeps_all_billed_usage(recover):
    from evals.judge import GroundingJudgment, validated_judgment

    requests = []

    def handler(request):
        payload = json.loads(request.content)
        requests.append(payload)
        # Valid JSON with a missing claim is still a failed judgment.
        value = (
            {"citations": [{"claim_index": 1, "supported": False, "reason": "Missing premise"}]}
            if recover and len(requests) == 2
            else {"citations": []}
        )
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": json.dumps(value)}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 110},
            },
        )

    metrics = Metrics({"judge_input": 2, "judge_output": 8})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = OpenAICompatibleProvider(client)
        args = (
            GroundingJudgment,
            [{"role": "user", "content": "untrusted data"}],
            Settings(),
            "fixture",
            provider,
            metrics,
            "grounding",
        )
        if recover:
            assert validated_judgment(*args, claim_count=1).citations[0].supported is False
        else:
            with pytest.raises(ModelError, match="after one format retry"):
                validated_judgment(*args, claim_count=1)
    assert len(requests) == 2
    assert "exactly 1 citations" in requests[1]["messages"][-1]["content"]
    assert len(metrics.validation_failures) == (1 if recover else 2)
    assert metrics.as_dict()["token_usage"]["total_tokens"] == 220
    assert metrics.as_dict()["cost_usd"] == pytest.approx(0.00056)


def test_compose_secret_survives_restart_and_explicit_sqlite_is_still_isolated(tmp_path, monkeypatch):
    initialize(tmp_path)
    secret = (tmp_path / "postgres_password").read_text()
    initialize(tmp_path)
    assert len(secret) > 30 and (tmp_path / "postgres_password").read_text() == secret
    monkeypatch.delenv("RAG_DATABASE_URL", raising=False)
    monkeypatch.setenv("RAG_DATABASE_PASSWORD_FILE", str(tmp_path / "postgres_password"))
    assert environment_database_url().startswith("postgresql://knowbase:")
    from backend.store import create_store

    assert create_store(tmp_path / "sqlite", database_url="").backend == "sqlite"
