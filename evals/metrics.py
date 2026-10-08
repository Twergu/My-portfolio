"""Transparent offline metrics; lexical proxies are never semantic correctness."""

import math
import re
import statistics
import unicodedata
from collections import Counter


def page_key(row):
    return str(row["document_id"]), int(row["page"])


def retrieval_metrics(sources, relevance, k):
    if k < 1:
        raise ValueError("k must be positive")
    grades = {page_key(row): row["grade"] for row in relevance if row["grade"] > 0}
    ranked, seen = [], set()
    for source in sources:
        key = page_key(source)
        if key not in seen:
            ranked.append(key)
            seen.add(key)
    ranked = ranked[:k]
    if not grades:
        return {
            "recall_at_k": None,
            "precision_at_k": None,
            "mrr_at_k": None,
            "ndcg_at_k": None,
            "retrieved_unique_pages": len(ranked),
            "any_retrieval_for_unanswerable": bool(ranked),
        }
    hits = [1 if key in grades else 0 for key in ranked]
    dcg = sum((2 ** grades.get(key, 0) - 1) / math.log2(i + 2) for i, key in enumerate(ranked))
    ideal = sum((2**grade - 1) / math.log2(i + 2) for i, grade in enumerate(sorted(grades.values(), reverse=True)[:k]))
    return {
        "recall_at_k": sum(hits) / len(grades),
        "precision_at_k": sum(hits) / k,
        "mrr_at_k": next((1 / (i + 1) for i, hit in enumerate(hits) if hit), 0.0),
        "ndcg_at_k": dcg / ideal,
        "retrieved_unique_pages": len(ranked),
        "any_retrieval_for_unanswerable": None,
    }


def normalized(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text).casefold())


def retrieval_at_cutoffs(sources, relevance, cutoffs=(1, 3, 5)):
    metrics = {}
    for k in cutoffs:
        # Apply the chunk budget before page deduplication; no extra chunks may
        # sneak into Recall@1/3 when the application retrieved 5 chunks.
        result = retrieval_metrics(sources[:k], relevance, k)
        for name in ("recall", "precision", "mrr", "ndcg"):
            metrics[f"{name}_at_{k}"] = result[f"{name}_at_k"]
    return metrics


def tokens(text):
    # CJK characters + Latin word tokens; deterministic and dependency-free.
    value = unicodedata.normalize("NFKC", re.sub(r"\[\d+\]", "", text)).casefold()
    return re.findall(r"[\u3040-\u30ff\u3400-\u9fff]|[a-z0-9]+", value)


def token_f1(actual, reference):
    actual_tokens, expected_tokens = Counter(tokens(actual)), Counter(tokens(reference))
    if not actual_tokens or not expected_tokens:
        return float(actual_tokens == expected_tokens)
    matches = sum((actual_tokens & expected_tokens).values())
    if not matches:
        return 0.0
    precision = matches / sum(actual_tokens.values())
    recall = matches / sum(expected_tokens.values())
    return 2 * precision * recall / (precision + recall)


def answer_metrics(result, query):
    names = (
        "expected_facts_coverage_lexical",
        "reference_token_f1_lexical",
        "reference_exact_match",
        "correct_refusal",
        "false_refusal",
        "claim_groundedness",
        "all_claims_grounded",
        "refusal_accuracy",
        "quote_match_failure",
        "unsupported_answer",
        "invalid_model_response",
        "generator_false_refusal",
        "grounding_false_refusal",
        "answer_correctness",
        "citation_groundedness",
    )
    if result.get("mode") != "api":
        return {
            "applicability": "N/A: local mode retrieves excerpts without generating answers",
            **dict.fromkeys(names),
        }
    status = result.get("status")
    # Safety rejection is not a successful insufficiency decision: otherwise a
    # provider returning broken answers for every question would score well.
    insufficient = status == "insufficient_evidence"
    answered = status == "answered"
    supported = [claim.get("supported") for claim in result.get("claims", [])]
    support = result.get("support") or {}
    coverage = None
    if query["answerable"]:
        facts = query["expected_facts"]
        text = normalized(result.get("answer", "")) if answered else ""
        coverage = (
            sum(any(normalized(alias) in text for alias in fact["aliases"]) for fact in facts) / len(facts)
            if facts
            else None
        )
    # A missing verification flag means unknown, rather than automatically true.
    total_claims, verified_claims = support.get("total_claims"), support.get("verified_claims")
    if (
        isinstance(total_claims, int)
        and not isinstance(total_claims, bool)
        and total_claims > 0
        and isinstance(verified_claims, int)
        and not isinstance(verified_claims, bool)
        and 0 <= verified_claims <= total_claims
    ):
        groundedness = verified_claims / total_claims
    else:
        groundedness = (
            sum(flag is True for flag in supported) / len(supported)
            if supported and all(isinstance(flag, bool) for flag in supported)
            else None
        )
    return {
        "applicability": "API only; lexical scores are proxies, groundedness uses verifier decisions",
        "expected_facts_coverage_lexical": coverage,
        "reference_token_f1_lexical": (
            token_f1(result.get("answer", ""), query["reference_answer"]) if answered else 0.0
        )
        if query["answerable"]
        else None,
        "reference_exact_match": (
            float(tokens(result.get("answer", "")) == tokens(query["reference_answer"])) if answered else 0.0
        )
        if query["answerable"]
        else None,
        "correct_refusal": float(insufficient) if not query["answerable"] else None,
        "false_refusal": float(not answered) if query["answerable"] else None,
        "refusal_accuracy": float(answered if query["answerable"] else insufficient),
        "quote_match_failure": float(support.get("failure_reason") == "quote_mismatch"),
        "unsupported_answer": float(status == "unsupported_answer"),
        "invalid_model_response": float(status == "invalid_model_response"),
        "generator_false_refusal": float(insufficient) if query["answerable"] else None,
        "grounding_false_refusal": float(status == "unsupported_answer") if query["answerable"] else None,
        "answer_correctness": None,
        "citation_groundedness": None,
        "claim_groundedness": groundedness,
        "all_claims_grounded": groundedness == 1 if groundedness is not None else None,
    }


def percentile(values, percent):
    values = sorted(value for value in values if value is not None)
    if not values:
        return None
    location = (len(values) - 1) * percent / 100
    low, high = math.floor(location), math.ceil(location)
    return values[low] + (values[high] - values[low]) * (location - low)


def distribution(values):
    values = [value for value in values if value is not None]
    return {
        "count": len(values),
        "mean": statistics.fmean(values) if values else None,
        "p50": percentile(values, 50),
        "p95": percentile(values, 95),
    }


def aggregate(rows):
    metrics = {}
    for section in ("retrieval", "answer_quality"):
        names = {
            name
            for row in rows
            for name, value in row[section].items()
            if isinstance(value, (int, float, bool)) or value is None
        }
        metrics[section] = {name: distribution([row[section].get(name) for row in rows]) for name in sorted(names)}
    phases = sorted({name for row in rows for name in row.get("metrics", {}).get("timings_ms", {})})
    metrics["latency_ms"] = {
        phase: distribution([row.get("metrics", {}).get("timings_ms", {}).get(phase) for row in rows])
        for phase in phases
    }
    metrics["latency_ms"]["question_total"] = distribution([row["elapsed_ms"] for row in rows])
    costs = [row.get("metrics", {}).get("cost_usd") for row in rows]
    metrics["cost_usd"] = {
        "total": sum(costs) if costs and all(value is not None for value in costs) else None,
        "known_subtotal": sum(value for value in costs if value is not None),
        "unknown_questions": sum(value is None for value in costs),
        "per_question": distribution(costs),
    }
    metrics["cost_usd"]["average_per_query"] = (
        sum(costs) / len(costs) if costs and all(value is not None for value in costs) else None
    )
    usages = [row.get("metrics", {}).get("token_usage", {}) for row in rows]
    metrics["token_usage"] = {
        key: sum(u.get(key, 0) for u in usages)
        for key in ("embedding_tokens", "input_tokens", "output_tokens", "total_tokens")
    }
    metrics["token_usage"]["complete"] = bool(usages) and all(u.get("complete", False) for u in usages)
    metrics["query_count"] = len(rows)
    metrics["status_counts"] = dict(Counter(row["status"] for row in rows))
    return metrics
