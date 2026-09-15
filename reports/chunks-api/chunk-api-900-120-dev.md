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
| all_claims_grounded | 0.9000 | 40 |
| answer_correctness | 0.8333 | 42 |
| citation_groundedness | 1.0000 | 36 |
| claim_groundedness | 0.9250 | 40 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.1429 | 42 |
| generator_false_refusal | 0.0476 | 42 |
| grounding_false_refusal | 0.0952 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 4 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3771 | 42 |
| refusal_accuracy | 0.8889 | 54 |
| unsupported_answer | 0.0741 | 54 |
| withheld_candidate_correctness | 1.0000 | 4 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3386.4710 | 6650.6381 | 54 |
| provider_http | 5779.7885 | 11245.7059 | 54 |
| query_embedding | 307.5865 | 434.6291 | 54 |
| retrieval | 12.6585 | 13.2741 | 54 |
| verification | 2332.1785 | 4967.5869 | 40 |
| question_total | 5800.8790 | 11267.2034 | 54 |

Indexing: 96 chunks, 22949.62 ms.
Total run API cost (USD): 0.1902. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0008; reported tokens: {'embedding_tokens': 1582, 'input_tokens': 72389, 'output_tokens': 25022, 'total_tokens': 98993, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.145464, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 6159.72 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 5175.36 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 5386.09 |
| aster-en-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 2407.38 |
| aster-en-05 | negation | answered | 1.0000 | N/A | 6503.22 |
| aster-en-06 | exception | answered | 1.0000 | N/A | 6137.59 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 8954.63 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 5698.60 |
| aster-en-09 | cross_document | unsupported_answer | 0.6667 | N/A | 9237.59 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 10404.24 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 8962.97 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 7608.45 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 1790.76 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1252.37 |
| aster-en-15 | negative | insufficient_evidence | N/A | N/A | 1225.54 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1573.25 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 5244.49 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 6900.28 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 5620.82 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 6084.42 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 5903.16 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 12186.42 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 3907.83 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 7522.82 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 8764.50 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 10684.15 |
| aster-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 10645.99 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 8263.11 |
| aster-zh-11 | similar_document | answered | 1.0000 | N/A | 6081.78 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 1844.12 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 1928.89 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1887.58 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1680.48 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1851.40 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 5512.18 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 8235.37 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 6739.02 |
| aster-ja-02 | old_version | answered | 1.0000 | N/A | 5608.37 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 4719.14 |
| aster-ja-04 | numeric_trap | answered | 0.0000 | N/A | 9178.30 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 4447.92 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 5690.55 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 8285.41 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 7986.16 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 11996.19 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 11520.93 |
| aster-ja-11 | similar_document | answered | 1.0000 | N/A | 5620.92 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 7759.44 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 1827.29 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1540.42 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1200.45 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1381.83 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 5033.74 |
| aster-ja-18 | cross_document | answered | 0.5000 | N/A | 11130.58 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
