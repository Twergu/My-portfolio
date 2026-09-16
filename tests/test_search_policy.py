from backend.config import Settings
from backend.search_policy import ann_acceptance


def test_ann_gate_requires_actual_index_recall_and_speed():
    exact = {"status": "measured", "query_latency_ms": {"p95": 100}}
    ann = {
        "status": "measured",
        "hnsw_index_used": True,
        "query_latency_ms": {"p95": 10},
        "recall_at_k_against_independent_exact": 0.88,
    }
    assert not ann_acceptance(exact, ann)["eligible_for_corpus_review"]
    ann["recall_at_k_against_independent_exact"] = 0.96
    assert ann_acceptance(exact, ann)["eligible_for_corpus_review"]
    ann["hnsw_index_used"] = False
    assert not ann_acceptance(exact, ann)["eligible_for_corpus_review"]
    assert Settings().search_mode == "exact"
