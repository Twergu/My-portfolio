# RAG evaluation — policy-challenge-v2.1

Mode: **api**; split: **dev**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5992 | 42 |
| recall_at_3 | 0.8135 | 42 |
| recall_at_5 | 0.8810 | 42 |
| mrr_at_k | 0.8353 | 42 |
| ndcg_at_k | 0.8128 | 42 |
| precision_at_k | 0.2476 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | 0.9231 | 39 |
| answer_correctness | 0.8571 | 42 |
| citation_groundedness | 1.0000 | 36 |
| claim_groundedness | 0.9359 | 39 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.1429 | 42 |
| generator_false_refusal | 0.0714 | 42 |
| grounding_false_refusal | 0.0714 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 3 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3781 | 42 |
| refusal_accuracy | 0.8889 | 54 |
| unsupported_answer | 0.0556 | 54 |
| withheld_candidate_correctness | 1.0000 | 3 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3547.1170 | 6950.0146 | 54 |
| provider_http | 5848.9910 | 11424.6376 | 54 |
| query_embedding | 295.8660 | 403.5239 | 54 |
| retrieval | 25.3895 | 120.4880 | 54 |
| verification | 2483.3840 | 3999.5946 | 39 |
| question_total | 5988.0166 | 11451.9354 | 54 |

Indexing: 96 chunks, 24288.33 ms.
Total run API cost (USD): 0.1943. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0008; reported tokens: {'embedding_tokens': 1582, 'input_tokens': 72342, 'output_tokens': 24514, 'total_tokens': 98438, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.150168, 'judge_errors': 0, 'recovered_errors': 1}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 6397.12 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 5212.72 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 4988.62 |
| aster-en-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 4306.80 |
| aster-en-05 | negation | answered | 1.0000 | N/A | 7638.38 |
| aster-en-06 | exception | insufficient_evidence | 1.0000 | N/A | 3715.44 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 7272.22 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 5894.69 |
| aster-en-09 | cross_document | unsupported_answer | 0.6667 | N/A | 13871.92 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 9206.04 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 5979.80 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 6717.25 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 1703.61 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1469.93 |
| aster-en-15 | negative | insufficient_evidence | N/A | N/A | 1647.44 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1496.48 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 5126.39 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 9077.73 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 5626.17 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 4403.07 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 4686.85 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 9248.74 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 5407.26 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 5996.23 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 7594.27 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 8241.47 |
| aster-zh-09 | cross_document | answered | 0.6667 | N/A | 11395.73 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 7475.77 |
| aster-zh-11 | similar_document | answered | 1.0000 | N/A | 6757.36 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 2250.97 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 1905.94 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1791.01 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1890.20 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1831.39 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 5876.71 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 7847.47 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 8282.77 |
| aster-ja-02 | old_version | unsupported_answer | 1.0000 | N/A | 5066.97 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 5410.38 |
| aster-ja-04 | numeric_trap | answered | 0.0000 | N/A | 10374.07 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 7368.45 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 6326.93 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 6869.61 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 7168.36 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 9138.36 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 9434.68 |
| aster-ja-11 | similar_document | answered | 1.0000 | N/A | 6558.71 |
| aster-ja-12 | draft_trap | answered | 1.0000 | N/A | 11942.05 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 2792.37 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1514.78 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1149.75 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1378.51 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 6449.38 |
| aster-ja-18 | cross_document | answered | 0.5000 | N/A | 11556.31 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
