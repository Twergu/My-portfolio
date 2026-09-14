# RAG evaluation — policy-challenge-v2

Mode: **local**; split: **test**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5516 | 42 |
| recall_at_3 | 0.7500 | 42 |
| recall_at_5 | 0.8373 | 42 |
| mrr_at_k | 0.7865 | 42 |
| ndcg_at_k | 0.7505 | 42 |
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

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Groundedness reflects structured verifier judgments, not independent human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| query_embedding | 0.3255 | 0.3587 | 54 |
| retrieval | 10.3850 | 11.7931 | 54 |
| question_total | 17.8784 | 19.8091 | 54 |

Indexing: 100 chunks, 1013.20 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0000; reported tokens: {'embedding_tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'not_applicable', 'judge_cost_usd': 0.0, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | retrieval_only | 0.0000 | N/A | 19.79 |
| boreal-en-02 | old_version | retrieval_only | 1.0000 | N/A | 17.31 |
| boreal-en-03 | similar_document | retrieval_only | 1.0000 | N/A | 17.58 |
| boreal-en-04 | numeric_trap | retrieval_only | 1.0000 | N/A | 19.68 |
| boreal-en-05 | negation | retrieval_only | 1.0000 | N/A | 18.63 |
| boreal-en-06 | exception | retrieval_only | 1.0000 | N/A | 17.86 |
| boreal-en-07 | exception_denied | retrieval_only | 0.5000 | N/A | 18.59 |
| boreal-en-08 | negation | retrieval_only | 1.0000 | N/A | 17.90 |
| boreal-en-09 | cross_document | retrieval_only | 0.3333 | N/A | 18.03 |
| boreal-en-10 | cross_document | retrieval_only | 1.0000 | N/A | 17.86 |
| boreal-en-11 | similar_document | retrieval_only | 1.0000 | N/A | 19.48 |
| boreal-en-12 | draft_trap | retrieval_only | 1.0000 | N/A | 19.02 |
| boreal-en-13 | negative | retrieval_only | N/A | N/A | 17.91 |
| boreal-en-14 | negative | retrieval_only | N/A | N/A | 19.38 |
| boreal-en-15 | negative | retrieval_only | N/A | N/A | 17.78 |
| boreal-en-16 | adversarial | retrieval_only | N/A | N/A | 13.78 |
| boreal-en-17 | negation | retrieval_only | 1.0000 | N/A | 19.33 |
| boreal-en-18 | cross_document | retrieval_only | 1.0000 | N/A | 17.57 |
| boreal-zh-01 | current_version | retrieval_only | 1.0000 | N/A | 19.05 |
| boreal-zh-02 | old_version | retrieval_only | 1.0000 | N/A | 18.19 |
| boreal-zh-03 | similar_document | retrieval_only | 1.0000 | N/A | 17.44 |
| boreal-zh-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 17.72 |
| boreal-zh-05 | negation | retrieval_only | 1.0000 | N/A | 17.92 |
| boreal-zh-06 | exception | retrieval_only | 1.0000 | N/A | 17.97 |
| boreal-zh-07 | exception_denied | retrieval_only | 0.5000 | N/A | 17.61 |
| boreal-zh-08 | negation | retrieval_only | 1.0000 | N/A | 18.38 |
| boreal-zh-09 | cross_document | retrieval_only | 0.6667 | N/A | 18.05 |
| boreal-zh-10 | cross_document | retrieval_only | 1.0000 | N/A | 17.61 |
| boreal-zh-11 | similar_document | retrieval_only | 1.0000 | N/A | 17.32 |
| boreal-zh-12 | draft_trap | retrieval_only | 0.5000 | N/A | 17.06 |
| boreal-zh-13 | negative | retrieval_only | N/A | N/A | 18.54 |
| boreal-zh-14 | negative | retrieval_only | N/A | N/A | 17.52 |
| boreal-zh-15 | negative | retrieval_only | N/A | N/A | 14.74 |
| boreal-zh-16 | adversarial | retrieval_only | N/A | N/A | 15.41 |
| boreal-zh-17 | negation | retrieval_only | 1.0000 | N/A | 17.76 |
| boreal-zh-18 | cross_document | retrieval_only | 0.5000 | N/A | 17.81 |
| boreal-ja-01 | current_version | retrieval_only | 1.0000 | N/A | 18.59 |
| boreal-ja-02 | old_version | retrieval_only | 1.0000 | N/A | 18.42 |
| boreal-ja-03 | similar_document | retrieval_only | 1.0000 | N/A | 17.87 |
| boreal-ja-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 18.09 |
| boreal-ja-05 | negation | retrieval_only | 1.0000 | N/A | 20.12 |
| boreal-ja-06 | exception | retrieval_only | 1.0000 | N/A | 17.70 |
| boreal-ja-07 | exception_denied | retrieval_only | 0.5000 | N/A | 17.53 |
| boreal-ja-08 | negation | retrieval_only | 1.0000 | N/A | 17.06 |
| boreal-ja-09 | cross_document | retrieval_only | 0.6667 | N/A | 17.47 |
| boreal-ja-10 | cross_document | retrieval_only | 1.0000 | N/A | 19.84 |
| boreal-ja-11 | similar_document | retrieval_only | 1.0000 | N/A | 17.38 |
| boreal-ja-12 | draft_trap | retrieval_only | 1.0000 | N/A | 18.29 |
| boreal-ja-13 | negative | retrieval_only | N/A | N/A | 20.16 |
| boreal-ja-14 | negative | retrieval_only | N/A | N/A | 18.24 |
| boreal-ja-15 | negative | retrieval_only | N/A | N/A | 16.07 |
| boreal-ja-16 | adversarial | retrieval_only | N/A | N/A | 16.36 |
| boreal-ja-17 | negation | retrieval_only | 1.0000 | N/A | 17.06 |
| boreal-ja-18 | cross_document | retrieval_only | 1.0000 | N/A | 17.88 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
