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
| ndcg_at_k | 0.8109 | 42 |
| precision_at_k | 0.2476 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | 0.8293 | 41 |
| answer_correctness | 0.7857 | 42 |
| citation_groundedness | 1.0000 | 34 |
| claim_groundedness | 0.8780 | 41 |
| correct_refusal | 0.9167 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.2143 | 42 |
| generator_false_refusal | 0.0476 | 42 |
| grounding_false_refusal | 0.1667 | 42 |
| grounding_rejected_correct_and_grounded | 0.8571 | 7 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3450 | 42 |
| refusal_accuracy | 0.8148 | 54 |
| unsupported_answer | 0.1296 | 54 |
| withheld_candidate_correctness | 0.8571 | 7 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3222.5565 | 6370.5791 | 54 |
| provider_http | 5716.7090 | 11997.0235 | 54 |
| query_embedding | 325.9420 | 478.2662 | 54 |
| retrieval | 13.3005 | 14.3485 | 54 |
| verification | 2262.5900 | 4719.4570 | 41 |
| question_total | 5737.8147 | 12018.5834 | 54 |

Indexing: 96 chunks, 20143.28 ms.
Total run API cost (USD): 0.1958. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0009; reported tokens: {'embedding_tokens': 1582, 'input_tokens': 72624, 'output_tokens': 27453, 'total_tokens': 101659, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.148164, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 4205.15 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 4288.49 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 3190.01 |
| aster-en-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 4970.59 |
| aster-en-05 | negation | answered | 1.0000 | N/A | 6365.77 |
| aster-en-06 | exception | answered | 1.0000 | N/A | 6161.17 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 5571.72 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 7959.87 |
| aster-en-09 | cross_document | unsupported_answer | 0.6667 | N/A | 10308.92 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 7546.02 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 4464.96 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 8404.90 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 2098.53 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1275.68 |
| aster-en-15 | negative | answered | N/A | N/A | 4191.73 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1445.38 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 4681.66 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 7860.63 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 8668.81 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 5227.01 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 5183.44 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 15624.25 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 6672.39 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 6833.39 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 8601.49 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 7894.64 |
| aster-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 10179.18 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 7978.79 |
| aster-zh-11 | similar_document | answered | 1.0000 | N/A | 5128.85 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 2412.23 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 2141.50 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1774.99 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1374.62 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1529.53 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 5052.77 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 6423.93 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 6184.80 |
| aster-ja-02 | old_version | unsupported_answer | 1.0000 | N/A | 4338.54 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 5903.91 |
| aster-ja-04 | numeric_trap | answered | 0.0000 | N/A | 8145.66 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 5037.90 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 5530.72 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 7333.01 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 6609.30 |
| aster-ja-09 | cross_document | unsupported_answer | 0.6667 | N/A | 11826.73 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 7934.72 |
| aster-ja-11 | similar_document | answered | 1.0000 | N/A | 6632.38 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 12374.88 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 2160.40 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1515.78 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1094.01 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1496.16 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 6033.50 |
| aster-ja-18 | cross_document | unsupported_answer | 0.5000 | N/A | 14266.53 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
