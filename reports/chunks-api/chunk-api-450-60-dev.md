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
| ndcg_at_k | 0.8123 | 42 |
| precision_at_k | 0.2524 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | 0.8250 | 40 |
| answer_correctness | 0.7619 | 42 |
| citation_groundedness | 1.0000 | 33 |
| claim_groundedness | 0.8500 | 40 |
| correct_refusal | 0.9167 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.2381 | 42 |
| generator_false_refusal | 0.0714 | 42 |
| grounding_false_refusal | 0.1667 | 42 |
| grounding_rejected_correct_and_grounded | 0.8571 | 7 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3293 | 42 |
| refusal_accuracy | 0.7963 | 54 |
| unsupported_answer | 0.1296 | 54 |
| withheld_candidate_correctness | 1.0000 | 7 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3210.5865 | 6424.1342 | 54 |
| provider_http | 5807.7680 | 10369.8617 | 54 |
| query_embedding | 284.5365 | 434.6642 | 54 |
| retrieval | 27.6065 | 210.9366 | 54 |
| verification | 2705.1145 | 4469.9575 | 40 |
| question_total | 5991.3406 | 10409.0792 | 54 |

Indexing: 100 chunks, 16635.57 ms.
Total run API cost (USD): 0.1879. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0008; reported tokens: {'embedding_tokens': 1582, 'input_tokens': 72118, 'output_tokens': 24077, 'total_tokens': 97777, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.144386, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 4630.56 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 3996.05 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 5738.06 |
| aster-en-04 | numeric_trap | answered | 1.0000 | N/A | 5940.10 |
| aster-en-05 | negation | answered | 1.0000 | N/A | 7655.40 |
| aster-en-06 | exception | answered | 1.0000 | N/A | 4900.28 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 5457.16 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 9313.25 |
| aster-en-09 | cross_document | insufficient_evidence | 0.6667 | N/A | 2075.65 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 7668.07 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 5270.85 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 7654.67 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 1765.64 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1571.02 |
| aster-en-15 | negative | answered | N/A | N/A | 5278.07 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1335.45 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 6894.12 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 10639.97 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 11633.97 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 4997.86 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 4877.72 |
| aster-zh-04 | numeric_trap | unsupported_answer | 0.0000 | N/A | 10078.07 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 7475.88 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 8125.52 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 7470.04 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 9056.03 |
| aster-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 7628.07 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 8687.31 |
| aster-zh-11 | similar_document | unsupported_answer | 1.0000 | N/A | 7927.58 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 2132.01 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 1642.15 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1955.75 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1413.29 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1703.14 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 5635.36 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 6921.36 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 7696.13 |
| aster-ja-02 | old_version | answered | 1.0000 | N/A | 5378.37 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 5528.03 |
| aster-ja-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 6042.58 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 9250.62 |
| aster-ja-06 | exception | unsupported_answer | 1.0000 | N/A | 7238.65 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 7418.71 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 9964.34 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 11425.82 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 9144.55 |
| aster-ja-11 | similar_document | unsupported_answer | 1.0000 | N/A | 8261.89 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 8467.69 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 1933.22 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1534.00 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1448.97 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1980.83 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 5646.91 |
| aster-ja-18 | cross_document | answered | 0.5000 | N/A | 10284.75 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
