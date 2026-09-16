import json
from pathlib import Path

import pytest

from backend.verification import needs_semantic_verification
from scripts.calibrate_verifier import classification


def test_calibration_blind_labels_and_balanced_splits():
    data = json.loads(Path("evals/claim_calibration.json").read_text(encoding="utf-8"))
    assert "AI-authored" in data["review_status"]
    cases = data["cases"]
    assert len({c["id"] for c in cases}) == len(cases)
    for split in ("dev", "test"):
        rows = [c for c in cases if c["split"] == split]
        assert len(rows) == 18
        assert {c["language"] for c in rows} == {"zh", "ja", "en"}
        assert {c["supported"] for c in rows} == {True, False}


def test_confusion_matrix_excludes_protocol_errors_not_counts_as_refusal():
    rows = [
        {"expected": a, "predicted": b}
        for a, b in [(True, True), (True, False), (False, True), (False, False), (False, None)]
    ]
    result = classification(rows)
    assert result["precision"] == result["recall"] == 0.5
    assert result["errors"] == 1


@pytest.mark.parametrize(
    "text",
    [
        "The cap is 5 dollars.",
        "Meals are not reimbursed.",
        "草案尚未批准。",
        "税込みです。",
        "申請できません。",
        "Only managers may approve.",
    ],
)
def test_selective_always_checks_risky_even_verbatim(text):
    claim = {"text": text, "cited_passages": [{"quote": text, "text": text}]}
    assert needs_semantic_verification("Explain the policy.", claim)


def test_selective_skips_only_simple_full_excerpts_and_checks_question_scope():
    claim = {
        "text": "Contact the support desk.",
        "cited_passages": [{"quote": "Contact the support desk.", "text": "Contact the support desk."}],
    }
    assert not needs_semantic_verification("Who handles enquiries?", claim)
    assert needs_semantic_verification("Who handles enquiries in 2026?", claim)
    claim["text"] = "The support desk responds instantly."
    assert needs_semantic_verification("Who handles enquiries?", claim)


def test_selective_delivery_marks_skips_unknown(monkeypatch):
    from backend import rag
    from backend.config import Settings

    text = "Contact the support desk."
    source = {"number": 1, "text": text, "name": "Help", "page": 1}
    monkeypatch.setattr(rag, "retrieve", lambda *a, **kw: [source])

    class Provider:
        def chat(self, *args, **kwargs):
            assert kwargs.get("role") != "verifier"
            return json.dumps(
                {"status": "answered", "claims": [{"text": text, "evidence": [{"source_id": 1, "quote": text}]}]}
            )

    result = rag.answer(
        None,
        "Who handles enquiries?",
        Settings(mode="api", verification_strategy="selective"),
        "",
        None,
        provider=Provider(),
    )
    assert result["status"] == "answered"
    assert result["claims"][0]["supported"] is None
    assert result["support"]["all_supported"] is None
    assert result["support"]["verified_claims"] is None
    assert result["support"]["skipped_claim_indices"] == [1]
