"""Report-only ANN acceptance gate. It never changes production configuration."""


def ann_acceptance(exact, candidate, minimum_recall=0.95):
    if not 0 < minimum_recall <= 1:
        raise ValueError("minimum_recall must be in (0,1]")
    recall = candidate.get("recall_at_k_against_independent_exact")
    exact_p95 = exact.get("query_latency_ms", {}).get("p95")
    ann_p95 = candidate.get("query_latency_ms", {}).get("p95")
    measured = candidate.get("status") == exact.get("status") == "measured" and candidate.get("hnsw_index_used") is True
    recall_pass = measured and recall is not None and recall >= minimum_recall
    speed_pass = measured and exact_p95 is not None and ann_p95 is not None and ann_p95 < exact_p95
    return {
        "minimum_recall": minimum_recall,
        "recall_pass": bool(recall_pass),
        "p95_faster": bool(speed_pass),
        "eligible_for_corpus_review": bool(recall_pass and speed_pass),
        "automatic_default_change": False,
        "scope": "This measured corpus/query/filter set only; production and ACL-filtered recall need separate validation.",
    }
