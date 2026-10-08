# RAG evaluation — policy-challenge-v2.1

Mode: **api**; split: **dev**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5873 | 42 |
| recall_at_3 | 0.8056 | 42 |
| recall_at_5 | 0.9048 | 42 |
| mrr_at_k | 0.8254 | 42 |
| ndcg_at_k | 0.8104 | 42 |
| precision_at_k | 0.2524 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | 0.8293 | 41 |
| answer_correctness | 0.8095 | 42 |
| citation_groundedness | 1.0000 | 34 |
| claim_groundedness | 0.8293 | 41 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.1905 | 42 |
| generator_false_refusal | 0.0238 | 42 |
| grounding_false_refusal | 0.1667 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 7 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3434 | 42 |
| refusal_accuracy | 0.8519 | 54 |
| unsupported_answer | 0.1296 | 54 |
| withheld_candidate_correctness | 1.0000 | 7 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 4018.8405 | 8008.4387 | 54 |
| provider_http | 5599.9410 | 10055.2535 | 54 |
| query_embedding | 291.0710 | 411.0546 | 54 |
| retrieval | 15.4090 | 33.6894 | 54 |
| verification | 1399.9820 | 2743.5810 | 41 |
| question_total | 5641.5755 | 10082.1213 | 54 |

Indexing: 100 chunks, 21026.40 ms.
Total run API cost (USD): 0.2019. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0009; reported tokens: {'embedding_tokens': 1582, 'input_tokens': 72786, 'output_tokens': 22915, 'total_tokens': 97283, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.153448, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 5381.50 |
| aster-en-02 | old_version | unsupported_answer | 1.0000 | N/A | 5664.16 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 4789.11 |
| aster-en-04 | numeric_trap | answered | 1.0000 | N/A | 6633.11 |
| aster-en-05 | negation | answered | 1.0000 | N/A | 7991.53 |
| aster-en-06 | exception | unsupported_answer | 1.0000 | N/A | 5747.95 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 4569.11 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 8507.71 |
| aster-en-09 | cross_document | answered | 0.6667 | N/A | 7561.60 |
| aster-en-10 | cross_document | unsupported_answer | 1.0000 | N/A | 5316.19 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 4315.75 |
| aster-en-12 | draft_trap | answered | 1.0000 | N/A | 5243.86 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 1562.99 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1470.63 |
| aster-en-15 | negative | insufficient_evidence | N/A | N/A | 1480.77 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1672.45 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 7128.43 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 8910.43 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 6345.25 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 4082.84 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 4811.55 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 9998.79 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 7573.74 |
| aster-zh-06 | exception | unsupported_answer | 1.0000 | N/A | 7198.46 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 9196.56 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 7357.04 |
| aster-zh-09 | cross_document | answered | 0.6667 | N/A | 9019.69 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 7838.67 |
| aster-zh-11 | similar_document | answered | 1.0000 | N/A | 4597.09 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 2247.80 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 2782.57 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 2064.78 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1688.38 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 2125.05 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 4968.79 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 7139.68 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 5618.99 |
| aster-ja-02 | old_version | answered | 1.0000 | N/A | 5842.61 |
| aster-ja-03 | similar_document | unsupported_answer | 1.0000 | N/A | 4630.73 |
| aster-ja-04 | numeric_trap | answered | 0.0000 | N/A | 12427.99 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 5691.60 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 5964.82 |
| aster-ja-07 | exception_denied | unsupported_answer | 1.0000 | N/A | 10247.73 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 9777.32 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 9532.85 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 6016.61 |
| aster-ja-11 | similar_document | answered | 1.0000 | N/A | 5528.03 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 7506.05 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 1914.39 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1370.68 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 2073.84 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1550.12 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 5265.18 |
| aster-ja-18 | cross_document | answered | 0.5000 | N/A | 10236.88 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
