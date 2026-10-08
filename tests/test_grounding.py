"""Adversarial grounding and failure observability checks, without paid calls."""

import json
from types import SimpleNamespace

import httpx
import pytest

from backend import rag
from backend.config import Settings
from backend.main import KnowledgeService
from backend.providers import OpenAICompatibleProvider
from backend.store import Store

SOURCE = (
    "Employees must request leave at least 3 working days in advance. "
    "Manager approval is required. The code NO_EVIDENCE is a literal status label."
)
QUOTE = "Employees must request leave at least 3 working days in advance."


def generated(claim="Leave requires a request at least 3 working days in advance.", quote=QUOTE):
    return {"status": "answered", "claims": [{"text": claim, "evidence": [{"source_id": 1, "quote": quote}]}]}


def verdict(supported=True):
    return {"verdicts": [{"claim_index": 1, "supported": supported, "reason": "Evidence checked."}]}


@pytest.fixture
def run_grounding(tmp_path):
    settings = Settings(mode="api", base_url="https://provider.example/v1", min_score=0)
    store = Store(tmp_path / "knowledge")
    store.register_document(
        {
            "id": "handbook",
            "name": "handbook.pdf",
            "sha256": "fixture",
            "size": 1,
            "status": "queued",
            "created_at": "2026-09-14T00:00:00Z",
        }
    )
    store.commit_chunks("handbook", [{"page": 2, "ordinal": 0, "text": SOURCE}], [[1.0, 0.0]], settings.profile)

    def run(generation, verification=None, mode="strict", verifier_model="", include_candidate=False):
        settings.verification_mode = mode
        settings.verifier_model = verifier_model
        requests = []
        chats = []

        def handler(request):
            payload = json.loads(request.content)
            requests.append((request.url.path, payload))
            if request.url.path.endswith("/embeddings"):
                return httpx.Response(
                    200,
                    json={
                        "data": [{"index": 0, "embedding": [1.0, 0.0]}],
                        "usage": {"prompt_tokens": 5, "total_tokens": 5},
                    },
                )
            chats.append(payload)
            answer = generation if len(chats) == 1 else verification
            if answer is None:
                pytest.fail("No verification request should be sent for invalid/missing quotes or a refusal.")
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": json.dumps(answer)}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
                },
            )

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            provider = OpenAICompatibleProvider(client)
            result = rag.answer(
                store,
                "How should employees request leave?",
                settings,
                "test-key",
                ["handbook"],
                preferred_language="en",
                provider=provider,
                include_candidate=include_candidate,
            )
        return result, requests, chats

    yield run
    store.close()


def test_withheld_candidate_only_available_to_explicit_evaluation(run_grounding):
    public, _, _ = run_grounding(generated(), verdict(False))
    assert public["status"] == "unsupported_answer"
    assert public["claims"] == [] and "evaluation_candidate" not in public
    evaluation, _, _ = run_grounding(generated(), verdict(False), include_candidate=True)
    assert evaluation["claims"] == []
    assert evaluation["evaluation_candidate"]["claims"][0]["text"] == generated()["claims"][0]["text"]
    assert evaluation["evaluation_candidate"]["sources"][0]["text"] == SOURCE


@pytest.mark.parametrize(
    "mode,expected", [("off", "answered"), ("fast", "unsupported_answer"), ("strict", "unsupported_answer")]
)
def test_modes_reject_or_expose_unverified_fabricated_quotes(run_grounding, mode, expected):
    result, _, chats = run_grounding(generated(quote="A fabricated quote that is not in the PDF."), mode=mode)
    assert result["status"] == expected
    assert len(chats) == 1
    if mode == "off":
        assert result["claims"][0]["supported"] is None
        assert result["support"]["all_supported"] is None
    else:
        assert result["support"]["failure_reason"] == "quote_mismatch"


def test_fast_mode_does_not_claim_semantic_verification(run_grounding):
    result, _, chats = run_grounding(generated(), mode="fast")
    assert len(chats) == 1 and result["status"] == "answered"
    assert result["support"]["method"] == "quote_match_only"
    assert result["support"]["verified_claims"] is None


def test_separate_verifier_is_routed_without_changing_embedding_profile(run_grounding):
    result, _, chats = run_grounding(generated(), verdict(), verifier_model="separate-verifier")
    assert result["status"] == "answered"
    assert chats[0]["model"] != chats[1]["model"] == "separate-verifier"
    assert "role" not in chats[1]
    assert result["support"]["verifier_model"] == "separate-verifier"
    assert Settings().profile == Settings(verifier_model="another", verification_mode="fast").profile


def test_real_quote_with_contradictory_claim_is_withheld_by_verifier(run_grounding):
    contradiction = "Employees can take leave immediately without manager approval."
    result, requests, chats = run_grounding(generated(contradiction), verdict(False))
    assert len(chats) == 2 and len(requests) == 3
    assert result["refused"] and result["status"] == "unsupported_answer"
    assert contradiction not in result["answer"] and not result["claims"] and not result["sources"]
    assert result["support"]["verified_claims"] == 0
    assert result["support"]["method"] == "quote_match_and_model_entailment"
    assert result["retrieved_sources"][0]["page"] == 2
    judge_input = json.loads(chats[1]["messages"][1]["content"])
    assert (
        judge_input["claims"][0]["cited_passages"][0]["text"] == SOURCE
    )  # Full context, restricted to the claim's actual cited sources.
    assert "sources" not in judge_input  # Uncited passages cannot accidentally justify the claim.
    assert result["metrics"]["attempt_count"] == 3
    assert set(result["metrics"]["timings_ms"]) >= {"query_embedding", "retrieval", "generation", "verification"}


def test_fabricated_quote_is_blocked_before_verifier(run_grounding):
    result, _, chats = run_grounding(generated(quote="Employees may always take leave without approval."))
    assert len(chats) == 1
    assert result["status"] == "unsupported_answer" and result["refused"]
    assert result["support"]["method"] == "quote_match"


@pytest.mark.parametrize(
    "verification",
    [
        {"verdicts": []},
        {"verdicts": [verdict()["verdicts"][0], verdict()["verdicts"][0]]},
        {"verdicts": [{"claim_index": 1, "supported": "true", "reason": "Claim supported."}]},
        {"verdicts": [{"claim_index": "1", "supported": True, "reason": "Claim supported."}]},
        {"verdicts": [{"claim_index": 2, "supported": True, "reason": "Claim supported."}]},
        {**verdict(), "answer": "Extra unverified conclusion."},
        {"verdicts": [{**verdict()["verdicts"][0], "extra": "unknown"}]},
    ],
)
def test_incomplete_duplicate_or_coerced_verdict_never_passes(run_grounding, verification):
    result, _, _ = run_grounding(generated(), verification)
    assert result["status"] == "unsupported_answer" and result["refused"]
    assert result["support"]["verified_claims"] == 0 and not result["support"]["all_supported"]
    assert not result["sources"] and not result["claims"]


def test_verdict_must_cover_every_claim(run_grounding):
    answer = generated()
    answer["claims"].append(
        {
            "text": "Manager approval is required.",
            "evidence": [{"source_id": 1, "quote": "Manager approval is required."}],
        }
    )
    result, _, _ = run_grounding(answer, verdict())
    assert result["support"]["total_claims"] == 2
    assert result["status"] == "unsupported_answer"


@pytest.mark.parametrize(
    "generation",
    [
        {**generated(), "answer": "Unverified extra text."},
        {"status": "answered", "claims": [{**generated()["claims"][0], "supported": True}]},
        {
            "status": "answered",
            "claims": [
                {
                    "text": "Manager approval is required.",
                    "evidence": [{"source_id": 1, "quote": QUOTE, "filename": "invented.pdf"}],
                }
            ],
        },
        {"status": "answered", "claims": []},
        {"status": "insufficient_evidence", "claims": generated()["claims"]},
        {
            "status": "answered",
            "claims": [{"text": "Manager approval is required.", "evidence": [{"source_id": True, "quote": QUOTE}]}],
        },
    ],
)
def test_extra_fields_and_incoherent_json_are_rejected(run_grounding, generation):
    result, _, chats = run_grounding(generation)
    assert len(chats) == 1 and result["status"] == "invalid_model_response"
    assert result["refused"] and not result["sources"]


def test_structured_insufficient_evidence_skips_verification(run_grounding):
    result, _, chats = run_grounding({"status": "insufficient_evidence", "claims": []})
    assert result["status"] == "insufficient_evidence" and result["refused"]
    assert result["support"]["method"] == "not_checked"
    assert len(chats) == 1 and result["sources"] == []


def test_literal_old_refusal_marker_has_no_control_semantics(run_grounding):
    text = "The code NO_EVIDENCE is a literal status label."
    result, _, _ = run_grounding(generated(text, text), verdict())
    assert result["status"] == "answered" and not result["refused"]
    assert result["answer"] == text + " [1]"
    assert result["sources"][0]["url"].endswith("#page=2")
    assert result["claims"][0]["supported"] is True


def test_indexing_logs_actual_traceback_with_document_and_stage(tmp_path, monkeypatch):
    class BrokenProvider:
        def embed(self, *args, **kwargs):
            raise RuntimeError("storage-independent embedding failure")

        def close(self):
            pass

    parsed = {"pages": [{"page": 1, "text": "A readable fixture passage."}], "empty_pages": []}
    monkeypatch.setattr(
        "backend.main.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(stdout=json.dumps(parsed).encode(), stderr=b"", returncode=0),
    )
    service = KnowledgeService(tmp_path / "logs-case", database_url="", provider=BrokenProvider())
    try:
        service.settings = Settings(mode="api")
        doc_id = service.register("broken.pdf", b"%PDF-1.7\nfixture")["id"]
        service.process(doc_id)
        service.log_handler.flush()
        contents = (service.store.folder / "logs" / "service.log").read_text(encoding="utf-8")
        assert "Traceback (most recent call last)" in contents
        assert "RuntimeError: storage-independent embedding failure" in contents
        assert f"document_id={doc_id}" in contents and "stage=embedding" in contents
        assert service.store.document(doc_id)["status"] == "error"
        measurement = service.measurements[-1]
        assert measurement["operation"] == "indexing" and measurement["status"] == "error"
        assert measurement["metrics"]["timings_ms"]["embedding"] >= 0
    finally:
        service.close()
