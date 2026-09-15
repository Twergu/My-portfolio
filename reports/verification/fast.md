# RAG evaluation — policy-challenge-v2.1

Mode: **api**; split: **test**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5833 | 42 |
| recall_at_3 | 0.8452 | 42 |
| recall_at_5 | 0.8810 | 42 |
| mrr_at_k | 0.8254 | 42 |
| ndcg_at_k | 0.8055 | 42 |
| precision_at_k | 0.2476 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | N/A | 0 |
| answer_correctness | 0.9286 | 42 |
| citation_groundedness | 1.0000 | 41 |
| claim_groundedness | N/A | 0 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.0238 | 42 |
| generator_false_refusal | 0.0238 | 42 |
| grounding_false_refusal | 0.0000 | 42 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.4138 | 42 |
| refusal_accuracy | 0.9815 | 54 |
| unsupported_answer | 0.0000 | 54 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3044.0215 | 6667.4983 | 54 |
| provider_http | 3366.4920 | 6963.9756 | 54 |
| query_embedding | 303.8110 | 509.0630 | 54 |
| retrieval | 12.4795 | 12.8029 | 54 |
| question_total | 3389.1299 | 6984.6610 | 54 |

Indexing: 96 chunks, 18384.76 ms.
Total run API cost (USD): 0.1823. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0006; reported tokens: {'embedding_tokens': 1600, 'input_tokens': 51133, 'output_tokens': 17070, 'total_tokens': 69803, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.151348, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | answered | 1.0000 | N/A | 3137.03 |
| boreal-en-02 | old_version | answered | 1.0000 | N/A | 1890.65 |
| boreal-en-03 | similar_document | answered | 1.0000 | N/A | 2514.89 |
| boreal-en-04 | numeric_trap | answered | 0.0000 | N/A | 5759.36 |
| boreal-en-05 | negation | answered | 1.0000 | N/A | 3694.25 |
| boreal-en-06 | exception | answered | 1.0000 | N/A | 2815.89 |
| boreal-en-07 | exception_denied | answered | 1.0000 | N/A | 3697.25 |
| boreal-en-08 | negation | answered | 1.0000 | N/A | 3321.41 |
| boreal-en-09 | cross_document | answered | 0.6667 | N/A | 4428.41 |
| boreal-en-10 | cross_document | answered | 1.0000 | N/A | 3456.85 |
| boreal-en-11 | similar_document | answered | 1.0000 | N/A | 3287.91 |
| boreal-en-12 | draft_trap | answered | 1.0000 | N/A | 3523.63 |
| boreal-en-13 | negative | insufficient_evidence | N/A | N/A | 1613.48 |
| boreal-en-14 | negative | insufficient_evidence | N/A | N/A | 2090.05 |
| boreal-en-15 | negative | insufficient_evidence | N/A | N/A | 1584.48 |
| boreal-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1158.29 |
| boreal-en-17 | negation | answered | 1.0000 | N/A | 2511.86 |
| boreal-en-18 | cross_document | answered | 1.0000 | N/A | 5349.39 |
| boreal-zh-01 | current_version | answered | 1.0000 | N/A | 3575.37 |
| boreal-zh-02 | old_version | answered | 1.0000 | N/A | 3240.85 |
| boreal-zh-03 | similar_document | answered | 1.0000 | N/A | 3547.59 |
| boreal-zh-04 | numeric_trap | answered | 0.0000 | N/A | 5302.28 |
| boreal-zh-05 | negation | answered | 1.0000 | N/A | 2726.95 |
| boreal-zh-06 | exception | answered | 1.0000 | N/A | 7324.14 |
| boreal-zh-07 | exception_denied | answered | 1.0000 | N/A | 4159.76 |
| boreal-zh-08 | negation | answered | 1.0000 | N/A | 9490.28 |
| boreal-zh-09 | cross_document | answered | 0.6667 | N/A | 5324.64 |
| boreal-zh-10 | cross_document | answered | 1.0000 | N/A | 6711.37 |
| boreal-zh-11 | similar_document | answered | 1.0000 | N/A | 4125.50 |
| boreal-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 1751.49 |
| boreal-zh-13 | negative | insufficient_evidence | N/A | N/A | 1680.03 |
| boreal-zh-14 | negative | insufficient_evidence | N/A | N/A | 1552.42 |
| boreal-zh-15 | negative | insufficient_evidence | N/A | N/A | 1836.39 |
| boreal-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1659.34 |
| boreal-zh-17 | negation | answered | 1.0000 | N/A | 4471.92 |
| boreal-zh-18 | cross_document | answered | 1.0000 | N/A | 4291.84 |
| boreal-ja-01 | current_version | answered | 1.0000 | N/A | 3074.04 |
| boreal-ja-02 | old_version | answered | 1.0000 | N/A | 2549.23 |
| boreal-ja-03 | similar_document | answered | 1.0000 | N/A | 3494.72 |
| boreal-ja-04 | numeric_trap | answered | 0.0000 | N/A | 6801.87 |
| boreal-ja-05 | negation | answered | 1.0000 | N/A | 3297.62 |
| boreal-ja-06 | exception | answered | 1.0000 | N/A | 4307.12 |
| boreal-ja-07 | exception_denied | answered | 1.0000 | N/A | 4424.40 |
| boreal-ja-08 | negation | answered | 1.0000 | N/A | 3230.03 |
| boreal-ja-09 | cross_document | answered | 0.6667 | N/A | 5162.39 |
| boreal-ja-10 | cross_document | answered | 1.0000 | N/A | 8109.97 |
| boreal-ja-11 | similar_document | answered | 1.0000 | N/A | 4646.10 |
| boreal-ja-12 | draft_trap | answered | 1.0000 | N/A | 6665.32 |
| boreal-ja-13 | negative | insufficient_evidence | N/A | N/A | 1555.98 |
| boreal-ja-14 | negative | insufficient_evidence | N/A | N/A | 2163.00 |
| boreal-ja-15 | negative | insufficient_evidence | N/A | N/A | 1688.39 |
| boreal-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1465.04 |
| boreal-ja-17 | negation | answered | 1.0000 | N/A | 3205.61 |
| boreal-ja-18 | cross_document | answered | 0.5000 | N/A | 6100.13 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
