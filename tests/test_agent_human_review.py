"""Test review bookkeeping with fixtures, never claim these are human judgments."""

import copy
import json

import pytest

from backend.config import ROOT
from scripts.human_review_report import summarize
from scripts.prepare_agent_review import fingerprint


def fixtures():
    data = json.loads((ROOT / "evals/agent-human-review-v1.json").read_text(encoding="utf-8"))
    form = {
        "dataset_sha256": fingerprint(data),
        "reviewer": None,
        "human_attested": False,
        "reviewed_at": None,
        "cases": [
            {"id": c["id"], "answer_correct": None, "all_claims_supported": None, "reference_approved": None}
            for c in data["cases"]
        ],
    }
    return data, form


def signed_fixture():
    data, form = fixtures()
    form.update(reviewer="CONTROLLED-TEST-FIXTURE", human_attested=True, reviewed_at="2026-10-05T10:00:00+09:00")
    for row in form["cases"]:
        row.update(answer_correct=True, all_claims_supported=True, reference_approved=True)
    return data, form


def test_unreviewed_or_unsigned_rows_cannot_produce_human_metrics():
    data, form = fixtures()
    result = summarize(data, form)
    assert result["human_reviewed"] == 0 and result["candidate_correctness"] is None
    for row in form["cases"]:
        row.update(answer_correct=True, all_claims_supported=True, reference_approved=True)
    assert summarize(data, form)["human_reviewed"] == 0


def test_partial_review_is_not_full_evaluation_and_string_booleans_do_not_pass():
    data, form = signed_fixture()
    form["cases"][-1]["answer_correct"] = "true"
    result = summarize(data, form)
    assert result["human_reviewed"] == 7 and result["status"] == "pending_human_review"
    assert result["candidate_correctness"] is None


def test_disagreement_with_recorded_automatic_verdict_is_kept():
    data, form = signed_fixture()
    form["cases"][0].update(answer_correct=False, all_claims_supported=False)
    result = summarize(data, form)
    assert result["status"] == "reviewed" and result["frozen_verifier_agrees_on_H01"] is False
    assert result["candidate_correctness"] == 7 / 8
    form["cases"][0]["reference_approved"] = False
    assert summarize(data, form)["status"] == "needs_adjudication"
    assert summarize(data, form)["candidate_correctness"] is None


def test_stale_duplicate_or_unsigned_timestamp_annotations_are_rejected():
    data, form = signed_fixture()
    changed = copy.deepcopy(data)
    changed["cases"][0]["candidate"] = "Changed after review"
    with pytest.raises(ValueError, match="frozen dataset"):
        summarize(changed, form)
    form["cases"][1] = form["cases"][0]
    with pytest.raises(ValueError, match="exactly once"):
        summarize(data, form)
    data, form = signed_fixture()
    form["reviewed_at"] = "2026-10-05"
    with pytest.raises(ValueError, match="timezone-aware"):
        summarize(data, form)


def test_review_packet_keeps_the_actual_false_supported_claim():
    data, _ = fixtures()
    report = json.loads((ROOT / data["frozen_failure"]["report"]).read_text(encoding="utf-8"))
    case = next(c for c in report["cases"] if c["id"] == data["frozen_failure"]["case_id"])
    claim = case["turns"][-1]["claims"][0]
    assert data["cases"][0]["candidate"] == claim["text"]
    assert claim["supported"] is True  # The historic model mistake remains visible.
    assert data["status"] == "awaiting_human_review"


def test_calibration_does_not_hide_errors_in_precision_or_recall(tmp_path):
    from scripts.agent_human_calibration import save

    report = {
        "scope": "Controlled metrics fixture",
        "cases": [{"human_supported": True, "verdict": {"supported": True}, "matches_human": True} for _ in range(7)]
        + [{"human_supported": True, "error_type": "ModelError", "matches_human": False}],
    }
    save(report, tmp_path / "metrics.json")
    assert report["summary"]["errors"] == 1
    assert report["summary"]["precision"] is None and report["summary"]["recall"] is None
    assert report["summary"]["agreement"] == 7 / 8
