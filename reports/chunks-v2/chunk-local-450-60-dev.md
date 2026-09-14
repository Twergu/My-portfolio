# RAG evaluation — policy-challenge-v2.1

Mode: **local**; split: **dev**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5794 | 42 |
| recall_at_3 | 0.7143 | 42 |
| recall_at_5 | 0.8611 | 42 |
| mrr_at_k | 0.8123 | 42 |
| ndcg_at_k | 0.7707 | 42 |
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
| query_embedding | 0.3385 | 0.5826 | 54 |
| retrieval | 12.3655 | 17.1174 | 54 |
| question_total | 20.3892 | 61.0723 | 54 |

Indexing: 100 chunks, 1156.91 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0000; reported tokens: {'embedding_tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'not_applicable', 'judge_cost_usd': 0.0, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | retrieval_only | 0.0000 | N/A | 28.48 |
| aster-en-02 | old_version | retrieval_only | 1.0000 | N/A | 186.48 |
| aster-en-03 | similar_document | retrieval_only | 1.0000 | N/A | 362.80 |
| aster-en-04 | numeric_trap | retrieval_only | 1.0000 | N/A | 121.50 |
| aster-en-05 | negation | retrieval_only | 1.0000 | N/A | 20.33 |
| aster-en-06 | exception | retrieval_only | 1.0000 | N/A | 19.96 |
| aster-en-07 | exception_denied | retrieval_only | 0.5000 | N/A | 20.45 |
| aster-en-08 | negation | retrieval_only | 1.0000 | N/A | 20.58 |
| aster-en-09 | cross_document | retrieval_only | 0.3333 | N/A | 19.28 |
| aster-en-10 | cross_document | retrieval_only | 1.0000 | N/A | 20.05 |
| aster-en-11 | similar_document | retrieval_only | 1.0000 | N/A | 19.10 |
| aster-en-12 | draft_trap | retrieval_only | 1.0000 | N/A | 19.06 |
| aster-en-13 | negative | retrieval_only | N/A | N/A | 20.14 |
| aster-en-14 | negative | retrieval_only | N/A | N/A | 18.40 |
| aster-en-15 | negative | retrieval_only | N/A | N/A | 16.39 |
| aster-en-16 | adversarial | retrieval_only | N/A | N/A | 14.20 |
| aster-en-17 | negation | retrieval_only | 1.0000 | N/A | 22.90 |
| aster-en-18 | cross_document | retrieval_only | 1.0000 | N/A | 25.82 |
| aster-zh-01 | current_version | retrieval_only | 1.0000 | N/A | 27.08 |
| aster-zh-02 | old_version | retrieval_only | 1.0000 | N/A | 23.46 |
| aster-zh-03 | similar_document | retrieval_only | 1.0000 | N/A | 20.20 |
| aster-zh-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 20.78 |
| aster-zh-05 | negation | retrieval_only | 1.0000 | N/A | 20.12 |
| aster-zh-06 | exception | retrieval_only | 1.0000 | N/A | 19.75 |
| aster-zh-07 | exception_denied | retrieval_only | 1.0000 | N/A | 19.25 |
| aster-zh-08 | negation | retrieval_only | 1.0000 | N/A | 19.43 |
| aster-zh-09 | cross_document | retrieval_only | 0.6667 | N/A | 20.09 |
| aster-zh-10 | cross_document | retrieval_only | 1.0000 | N/A | 21.23 |
| aster-zh-11 | similar_document | retrieval_only | 1.0000 | N/A | 18.34 |
| aster-zh-12 | draft_trap | retrieval_only | 0.5000 | N/A | 20.27 |
| aster-zh-13 | negative | retrieval_only | N/A | N/A | 20.56 |
| aster-zh-14 | negative | retrieval_only | N/A | N/A | 21.56 |
| aster-zh-15 | negative | retrieval_only | N/A | N/A | 19.43 |
| aster-zh-16 | adversarial | retrieval_only | N/A | N/A | 19.13 |
| aster-zh-17 | negation | retrieval_only | 1.0000 | N/A | 25.32 |
| aster-zh-18 | cross_document | retrieval_only | 1.0000 | N/A | 28.53 |
| aster-ja-01 | current_version | retrieval_only | 1.0000 | N/A | 23.43 |
| aster-ja-02 | old_version | retrieval_only | 1.0000 | N/A | 28.24 |
| aster-ja-03 | similar_document | retrieval_only | 1.0000 | N/A | 21.79 |
| aster-ja-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 21.30 |
| aster-ja-05 | negation | retrieval_only | 1.0000 | N/A | 19.48 |
| aster-ja-06 | exception | retrieval_only | 1.0000 | N/A | 20.58 |
| aster-ja-07 | exception_denied | retrieval_only | 0.5000 | N/A | 20.13 |
| aster-ja-08 | negation | retrieval_only | 1.0000 | N/A | 19.78 |
| aster-ja-09 | cross_document | retrieval_only | 0.6667 | N/A | 19.26 |
| aster-ja-10 | cross_document | retrieval_only | 1.0000 | N/A | 20.19 |
| aster-ja-11 | similar_document | retrieval_only | 1.0000 | N/A | 19.04 |
| aster-ja-12 | draft_trap | retrieval_only | 1.0000 | N/A | 18.84 |
| aster-ja-13 | negative | retrieval_only | N/A | N/A | 20.83 |
| aster-ja-14 | negative | retrieval_only | N/A | N/A | 25.55 |
| aster-ja-15 | negative | retrieval_only | N/A | N/A | 22.79 |
| aster-ja-16 | adversarial | retrieval_only | N/A | N/A | 22.25 |
| aster-ja-17 | negation | retrieval_only | 1.0000 | N/A | 27.03 |
| aster-ja-18 | cross_document | retrieval_only | 1.0000 | N/A | 22.84 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
