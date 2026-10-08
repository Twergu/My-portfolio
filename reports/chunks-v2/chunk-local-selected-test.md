# RAG evaluation — policy-challenge-v2.1

Mode: **local**; split: **test**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5873 | 42 |
| recall_at_3 | 0.7500 | 42 |
| recall_at_5 | 0.8611 | 42 |
| mrr_at_k | 0.8302 | 42 |
| ndcg_at_k | 0.7819 | 42 |
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
| query_embedding | 0.3570 | 0.5124 | 54 |
| retrieval | 12.4975 | 13.5721 | 54 |
| question_total | 20.8548 | 22.7367 | 54 |

Indexing: 100 chunks, 1251.59 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0000; reported tokens: {'embedding_tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'not_applicable', 'judge_cost_usd': 0.0, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | retrieval_only | 0.0000 | N/A | 23.44 |
| boreal-en-02 | old_version | retrieval_only | 1.0000 | N/A | 20.88 |
| boreal-en-03 | similar_document | retrieval_only | 1.0000 | N/A | 20.97 |
| boreal-en-04 | numeric_trap | retrieval_only | 1.0000 | N/A | 22.90 |
| boreal-en-05 | negation | retrieval_only | 1.0000 | N/A | 22.39 |
| boreal-en-06 | exception | retrieval_only | 1.0000 | N/A | 21.16 |
| boreal-en-07 | exception_denied | retrieval_only | 0.5000 | N/A | 23.17 |
| boreal-en-08 | negation | retrieval_only | 1.0000 | N/A | 21.37 |
| boreal-en-09 | cross_document | retrieval_only | 0.3333 | N/A | 21.76 |
| boreal-en-10 | cross_document | retrieval_only | 1.0000 | N/A | 21.88 |
| boreal-en-11 | similar_document | retrieval_only | 1.0000 | N/A | 19.31 |
| boreal-en-12 | draft_trap | retrieval_only | 1.0000 | N/A | 20.60 |
| boreal-en-13 | negative | retrieval_only | N/A | N/A | 21.60 |
| boreal-en-14 | negative | retrieval_only | N/A | N/A | 20.15 |
| boreal-en-15 | negative | retrieval_only | N/A | N/A | 15.28 |
| boreal-en-16 | adversarial | retrieval_only | N/A | N/A | 16.11 |
| boreal-en-17 | negation | retrieval_only | 1.0000 | N/A | 21.24 |
| boreal-en-18 | cross_document | retrieval_only | 1.0000 | N/A | 20.23 |
| boreal-zh-01 | current_version | retrieval_only | 1.0000 | N/A | 21.15 |
| boreal-zh-02 | old_version | retrieval_only | 1.0000 | N/A | 22.41 |
| boreal-zh-03 | similar_document | retrieval_only | 1.0000 | N/A | 19.72 |
| boreal-zh-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 21.35 |
| boreal-zh-05 | negation | retrieval_only | 1.0000 | N/A | 21.24 |
| boreal-zh-06 | exception | retrieval_only | 1.0000 | N/A | 19.86 |
| boreal-zh-07 | exception_denied | retrieval_only | 1.0000 | N/A | 21.21 |
| boreal-zh-08 | negation | retrieval_only | 1.0000 | N/A | 20.80 |
| boreal-zh-09 | cross_document | retrieval_only | 0.6667 | N/A | 19.26 |
| boreal-zh-10 | cross_document | retrieval_only | 1.0000 | N/A | 19.55 |
| boreal-zh-11 | similar_document | retrieval_only | 1.0000 | N/A | 19.05 |
| boreal-zh-12 | draft_trap | retrieval_only | 0.5000 | N/A | 19.71 |
| boreal-zh-13 | negative | retrieval_only | N/A | N/A | 20.03 |
| boreal-zh-14 | negative | retrieval_only | N/A | N/A | 20.02 |
| boreal-zh-15 | negative | retrieval_only | N/A | N/A | 15.89 |
| boreal-zh-16 | adversarial | retrieval_only | N/A | N/A | 16.28 |
| boreal-zh-17 | negation | retrieval_only | 1.0000 | N/A | 21.20 |
| boreal-zh-18 | cross_document | retrieval_only | 1.0000 | N/A | 20.75 |
| boreal-ja-01 | current_version | retrieval_only | 1.0000 | N/A | 20.92 |
| boreal-ja-02 | old_version | retrieval_only | 1.0000 | N/A | 22.28 |
| boreal-ja-03 | similar_document | retrieval_only | 1.0000 | N/A | 20.54 |
| boreal-ja-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 20.91 |
| boreal-ja-05 | negation | retrieval_only | 1.0000 | N/A | 21.34 |
| boreal-ja-06 | exception | retrieval_only | 1.0000 | N/A | 20.98 |
| boreal-ja-07 | exception_denied | retrieval_only | 0.5000 | N/A | 21.67 |
| boreal-ja-08 | negation | retrieval_only | 1.0000 | N/A | 20.83 |
| boreal-ja-09 | cross_document | retrieval_only | 0.6667 | N/A | 22.65 |
| boreal-ja-10 | cross_document | retrieval_only | 1.0000 | N/A | 20.90 |
| boreal-ja-11 | similar_document | retrieval_only | 1.0000 | N/A | 19.58 |
| boreal-ja-12 | draft_trap | retrieval_only | 1.0000 | N/A | 19.30 |
| boreal-ja-13 | negative | retrieval_only | N/A | N/A | 22.54 |
| boreal-ja-14 | negative | retrieval_only | N/A | N/A | 20.06 |
| boreal-ja-15 | negative | retrieval_only | N/A | N/A | 18.43 |
| boreal-ja-16 | adversarial | retrieval_only | N/A | N/A | 18.30 |
| boreal-ja-17 | negation | retrieval_only | 1.0000 | N/A | 19.39 |
| boreal-ja-18 | cross_document | retrieval_only | 1.0000 | N/A | 20.31 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
