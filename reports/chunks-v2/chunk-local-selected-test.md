# RAG evaluation — policy-challenge-v2.1

Mode: **local**; split: **test**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5873 | 42 |
| recall_at_3 | 0.7619 | 42 |
| recall_at_5 | 0.8611 | 42 |
| mrr_at_k | 0.8302 | 42 |
| ndcg_at_k | 0.7823 | 42 |
| precision_at_k | 0.2381 | 42 |

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
| query_embedding | 0.3320 | 0.5447 | 54 |
| retrieval | 11.5765 | 13.2489 | 54 |
| question_total | 19.1931 | 21.5934 | 54 |

Indexing: 100 chunks, 1071.17 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0000; reported tokens: {'embedding_tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'not_applicable', 'judge_cost_usd': 0.0, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | retrieval_only | 0.0000 | N/A | 20.82 |
| boreal-en-02 | old_version | retrieval_only | 1.0000 | N/A | 18.44 |
| boreal-en-03 | similar_document | retrieval_only | 1.0000 | N/A | 19.19 |
| boreal-en-04 | numeric_trap | retrieval_only | 1.0000 | N/A | 21.69 |
| boreal-en-05 | negation | retrieval_only | 1.0000 | N/A | 20.46 |
| boreal-en-06 | exception | retrieval_only | 1.0000 | N/A | 20.52 |
| boreal-en-07 | exception_denied | retrieval_only | 0.5000 | N/A | 18.82 |
| boreal-en-08 | negation | retrieval_only | 1.0000 | N/A | 19.50 |
| boreal-en-09 | cross_document | retrieval_only | 0.3333 | N/A | 22.94 |
| boreal-en-10 | cross_document | retrieval_only | 1.0000 | N/A | 20.66 |
| boreal-en-11 | similar_document | retrieval_only | 1.0000 | N/A | 18.73 |
| boreal-en-12 | draft_trap | retrieval_only | 1.0000 | N/A | 24.89 |
| boreal-en-13 | negative | retrieval_only | N/A | N/A | 18.96 |
| boreal-en-14 | negative | retrieval_only | N/A | N/A | 18.77 |
| boreal-en-15 | negative | retrieval_only | N/A | N/A | 15.92 |
| boreal-en-16 | adversarial | retrieval_only | N/A | N/A | 13.91 |
| boreal-en-17 | negation | retrieval_only | 1.0000 | N/A | 19.22 |
| boreal-en-18 | cross_document | retrieval_only | 1.0000 | N/A | 18.22 |
| boreal-zh-01 | current_version | retrieval_only | 1.0000 | N/A | 20.01 |
| boreal-zh-02 | old_version | retrieval_only | 1.0000 | N/A | 18.97 |
| boreal-zh-03 | similar_document | retrieval_only | 1.0000 | N/A | 21.02 |
| boreal-zh-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 20.23 |
| boreal-zh-05 | negation | retrieval_only | 1.0000 | N/A | 19.22 |
| boreal-zh-06 | exception | retrieval_only | 1.0000 | N/A | 18.45 |
| boreal-zh-07 | exception_denied | retrieval_only | 1.0000 | N/A | 19.08 |
| boreal-zh-08 | negation | retrieval_only | 1.0000 | N/A | 21.54 |
| boreal-zh-09 | cross_document | retrieval_only | 0.6667 | N/A | 19.86 |
| boreal-zh-10 | cross_document | retrieval_only | 1.0000 | N/A | 19.16 |
| boreal-zh-11 | similar_document | retrieval_only | 1.0000 | N/A | 18.98 |
| boreal-zh-12 | draft_trap | retrieval_only | 0.5000 | N/A | 20.31 |
| boreal-zh-13 | negative | retrieval_only | N/A | N/A | 19.96 |
| boreal-zh-14 | negative | retrieval_only | N/A | N/A | 20.38 |
| boreal-zh-15 | negative | retrieval_only | N/A | N/A | 15.37 |
| boreal-zh-16 | adversarial | retrieval_only | N/A | N/A | 15.59 |
| boreal-zh-17 | negation | retrieval_only | 1.0000 | N/A | 20.01 |
| boreal-zh-18 | cross_document | retrieval_only | 1.0000 | N/A | 19.94 |
| boreal-ja-01 | current_version | retrieval_only | 1.0000 | N/A | 19.39 |
| boreal-ja-02 | old_version | retrieval_only | 1.0000 | N/A | 18.74 |
| boreal-ja-03 | similar_document | retrieval_only | 1.0000 | N/A | 20.26 |
| boreal-ja-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 20.03 |
| boreal-ja-05 | negation | retrieval_only | 1.0000 | N/A | 19.65 |
| boreal-ja-06 | exception | retrieval_only | 1.0000 | N/A | 19.20 |
| boreal-ja-07 | exception_denied | retrieval_only | 0.5000 | N/A | 18.92 |
| boreal-ja-08 | negation | retrieval_only | 1.0000 | N/A | 17.93 |
| boreal-ja-09 | cross_document | retrieval_only | 0.6667 | N/A | 19.47 |
| boreal-ja-10 | cross_document | retrieval_only | 1.0000 | N/A | 21.35 |
| boreal-ja-11 | similar_document | retrieval_only | 1.0000 | N/A | 18.82 |
| boreal-ja-12 | draft_trap | retrieval_only | 1.0000 | N/A | 18.03 |
| boreal-ja-13 | negative | retrieval_only | N/A | N/A | 18.66 |
| boreal-ja-14 | negative | retrieval_only | N/A | N/A | 18.40 |
| boreal-ja-15 | negative | retrieval_only | N/A | N/A | 16.21 |
| boreal-ja-16 | adversarial | retrieval_only | N/A | N/A | 16.31 |
| boreal-ja-17 | negation | retrieval_only | 1.0000 | N/A | 19.06 |
| boreal-ja-18 | cross_document | retrieval_only | 1.0000 | N/A | 18.56 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
