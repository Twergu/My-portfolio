# RAG evaluation — policy-challenge-v2.1

Mode: **local**; split: **dev**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5794 | 42 |
| recall_at_3 | 0.7024 | 42 |
| recall_at_5 | 0.8254 | 42 |
| mrr_at_k | 0.8004 | 42 |
| ndcg_at_k | 0.7511 | 42 |
| precision_at_k | 0.2286 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | N/A | 0 |
| answer_correctness | N/A | 0 |
| citation_groundedness | N/A | 0 |
| claim_groundedness | N/A | 0 |
| correct_refusal | N/A | 0 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | N/A | 0 |
| generator_false_refusal | N/A | 0 |
| grounding_false_refusal | N/A | 0 |
| invalid_model_response | N/A | 0 |
| quote_match_failure | N/A | 0 |
| reference_exact_match | N/A | 0 |
| reference_token_f1_lexical | N/A | 0 |
| refusal_accuracy | N/A | 0 |
| unsupported_answer | N/A | 0 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| query_embedding | 0.3690 | 0.6351 | 54 |
| retrieval | 13.2490 | 17.2492 | 54 |
| question_total | 21.9775 | 26.9728 | 54 |

Indexing: 96 chunks, 1214.84 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0000; reported tokens: {'embedding_tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'not_applicable', 'judge_cost_usd': 0.0, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | retrieval_only | 0.0000 | N/A | 23.42 |
| aster-en-02 | old_version | retrieval_only | 1.0000 | N/A | 20.66 |
| aster-en-03 | similar_document | retrieval_only | 1.0000 | N/A | 20.06 |
| aster-en-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 20.75 |
| aster-en-05 | negation | retrieval_only | 1.0000 | N/A | 23.66 |
| aster-en-06 | exception | retrieval_only | 1.0000 | N/A | 22.98 |
| aster-en-07 | exception_denied | retrieval_only | 0.5000 | N/A | 23.66 |
| aster-en-08 | negation | retrieval_only | 1.0000 | N/A | 25.52 |
| aster-en-09 | cross_document | retrieval_only | 0.3333 | N/A | 21.12 |
| aster-en-10 | cross_document | retrieval_only | 1.0000 | N/A | 21.10 |
| aster-en-11 | similar_document | retrieval_only | 1.0000 | N/A | 19.25 |
| aster-en-12 | draft_trap | retrieval_only | 0.5000 | N/A | 20.27 |
| aster-en-13 | negative | retrieval_only | N/A | N/A | 21.62 |
| aster-en-14 | negative | retrieval_only | N/A | N/A | 17.97 |
| aster-en-15 | negative | retrieval_only | N/A | N/A | 17.83 |
| aster-en-16 | adversarial | retrieval_only | N/A | N/A | 16.52 |
| aster-en-17 | negation | retrieval_only | 1.0000 | N/A | 22.24 |
| aster-en-18 | cross_document | retrieval_only | 1.0000 | N/A | 19.84 |
| aster-zh-01 | current_version | retrieval_only | 1.0000 | N/A | 21.88 |
| aster-zh-02 | old_version | retrieval_only | 1.0000 | N/A | 20.00 |
| aster-zh-03 | similar_document | retrieval_only | 1.0000 | N/A | 20.42 |
| aster-zh-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 21.05 |
| aster-zh-05 | negation | retrieval_only | 1.0000 | N/A | 24.73 |
| aster-zh-06 | exception | retrieval_only | 1.0000 | N/A | 26.33 |
| aster-zh-07 | exception_denied | retrieval_only | 1.0000 | N/A | 25.62 |
| aster-zh-08 | negation | retrieval_only | 1.0000 | N/A | 27.60 |
| aster-zh-09 | cross_document | retrieval_only | 0.6667 | N/A | 27.16 |
| aster-zh-10 | cross_document | retrieval_only | 1.0000 | N/A | 29.47 |
| aster-zh-11 | similar_document | retrieval_only | 1.0000 | N/A | 21.27 |
| aster-zh-12 | draft_trap | retrieval_only | 0.5000 | N/A | 21.08 |
| aster-zh-13 | negative | retrieval_only | N/A | N/A | 22.79 |
| aster-zh-14 | negative | retrieval_only | N/A | N/A | 21.19 |
| aster-zh-15 | negative | retrieval_only | N/A | N/A | 15.86 |
| aster-zh-16 | adversarial | retrieval_only | N/A | N/A | 16.81 |
| aster-zh-17 | negation | retrieval_only | 1.0000 | N/A | 23.46 |
| aster-zh-18 | cross_document | retrieval_only | 1.0000 | N/A | 23.05 |
| aster-ja-01 | current_version | retrieval_only | 1.0000 | N/A | 21.87 |
| aster-ja-02 | old_version | retrieval_only | 1.0000 | N/A | 22.07 |
| aster-ja-03 | similar_document | retrieval_only | 1.0000 | N/A | 19.73 |
| aster-ja-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 22.13 |
| aster-ja-05 | negation | retrieval_only | 1.0000 | N/A | 22.71 |
| aster-ja-06 | exception | retrieval_only | 1.0000 | N/A | 26.83 |
| aster-ja-07 | exception_denied | retrieval_only | 0.5000 | N/A | 26.87 |
| aster-ja-08 | negation | retrieval_only | 1.0000 | N/A | 22.21 |
| aster-ja-09 | cross_document | retrieval_only | 0.6667 | N/A | 22.31 |
| aster-ja-10 | cross_document | retrieval_only | 1.0000 | N/A | 24.69 |
| aster-ja-11 | similar_document | retrieval_only | 1.0000 | N/A | 22.46 |
| aster-ja-12 | draft_trap | retrieval_only | 1.0000 | N/A | 21.54 |
| aster-ja-13 | negative | retrieval_only | N/A | N/A | 21.41 |
| aster-ja-14 | negative | retrieval_only | N/A | N/A | 23.63 |
| aster-ja-15 | negative | retrieval_only | N/A | N/A | 19.80 |
| aster-ja-16 | adversarial | retrieval_only | N/A | N/A | 18.79 |
| aster-ja-17 | negation | retrieval_only | 1.0000 | N/A | 22.71 |
| aster-ja-18 | cross_document | retrieval_only | 1.0000 | N/A | 22.79 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
