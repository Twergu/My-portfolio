# RAG evaluation — policy-challenge-v2.1

Mode: **api**; split: **dev**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5873 | 42 |
| recall_at_3 | 0.8135 | 42 |
| recall_at_5 | 0.8810 | 42 |
| mrr_at_k | 0.8234 | 42 |
| ndcg_at_k | 0.8074 | 42 |
| precision_at_k | 0.2476 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | 0.8718 | 39 |
| answer_correctness | 0.7619 | 42 |
| citation_groundedness | 1.0000 | 34 |
| claim_groundedness | 0.8846 | 39 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.1905 | 42 |
| generator_false_refusal | 0.0714 | 42 |
| grounding_false_refusal | 0.1190 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 5 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3610 | 42 |
| refusal_accuracy | 0.8519 | 54 |
| unsupported_answer | 0.0926 | 54 |
| withheld_candidate_correctness | 1.0000 | 5 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3370.4480 | 6508.0446 | 54 |
| provider_http | 5818.1840 | 11007.5887 | 54 |
| query_embedding | 317.7055 | 447.0660 | 54 |
| retrieval | 12.7350 | 13.2534 | 54 |
| verification | 2310.8830 | 4681.0394 | 39 |
| question_total | 5839.2333 | 11028.4860 | 54 |

Indexing: 96 chunks, 18023.43 ms.
Total run API cost (USD): 0.1890. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0008; reported tokens: {'embedding_tokens': 1582, 'input_tokens': 71880, 'output_tokens': 25786, 'total_tokens': 99248, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.143478, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 4393.18 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 5465.23 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 4640.70 |
| aster-en-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 2812.33 |
| aster-en-05 | negation | insufficient_evidence | 1.0000 | N/A | 5912.72 |
| aster-en-06 | exception | answered | 1.0000 | N/A | 5560.84 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 6884.83 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 7471.61 |
| aster-en-09 | cross_document | answered | 0.6667 | N/A | 11401.54 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 6881.47 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 5761.42 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 7201.13 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 1378.21 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1280.69 |
| aster-en-15 | negative | insufficient_evidence | N/A | N/A | 1364.04 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1361.90 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 6533.46 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 8938.45 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 7523.03 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 5347.40 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 4616.02 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 13925.73 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 7119.81 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 5254.12 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 6469.45 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 6268.17 |
| aster-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 10034.56 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 7586.48 |
| aster-zh-11 | similar_document | unsupported_answer | 1.0000 | N/A | 8447.85 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 2394.09 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 2136.28 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1947.19 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1376.44 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1885.87 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 4161.43 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 9372.43 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 6656.78 |
| aster-ja-02 | old_version | unsupported_answer | 1.0000 | N/A | 6043.99 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 4446.57 |
| aster-ja-04 | numeric_trap | answered | 0.0000 | N/A | 15146.03 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 7009.42 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 5765.75 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 6686.19 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 5673.76 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 8783.18 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 6268.03 |
| aster-ja-11 | similar_document | answered | 1.0000 | N/A | 7578.51 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 10827.61 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 2211.00 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1292.88 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1105.33 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1358.09 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 4832.40 |
| aster-ja-18 | cross_document | answered | 0.5000 | N/A | 9607.46 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
