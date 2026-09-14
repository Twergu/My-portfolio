# RAG evaluation — policy-challenge-v2

Mode: **local**; split: **dev**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5556 | 42 |
| recall_at_3 | 0.7143 | 42 |
| recall_at_5 | 0.8016 | 42 |
| mrr_at_k | 0.7706 | 42 |
| ndcg_at_k | 0.7237 | 42 |
| precision_at_k | 0.2190 | 42 |

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
| query_embedding | 0.3155 | 0.3671 | 54 |
| retrieval | 9.7975 | 10.7224 | 54 |
| question_total | 17.6794 | 20.8409 | 54 |

Indexing: 96 chunks, 1062.61 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0000; reported tokens: {'embedding_tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'not_applicable', 'judge_cost_usd': 0.0, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | retrieval_only | 0.0000 | N/A | 18.17 |
| aster-en-02 | old_version | retrieval_only | 1.0000 | N/A | 16.77 |
| aster-en-03 | similar_document | retrieval_only | 1.0000 | N/A | 17.03 |
| aster-en-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 17.87 |
| aster-en-05 | negation | retrieval_only | 1.0000 | N/A | 17.69 |
| aster-en-06 | exception | retrieval_only | 1.0000 | N/A | 17.37 |
| aster-en-07 | exception_denied | retrieval_only | 0.5000 | N/A | 18.19 |
| aster-en-08 | negation | retrieval_only | 1.0000 | N/A | 17.22 |
| aster-en-09 | cross_document | retrieval_only | 0.3333 | N/A | 16.55 |
| aster-en-10 | cross_document | retrieval_only | 1.0000 | N/A | 21.46 |
| aster-en-11 | similar_document | retrieval_only | 1.0000 | N/A | 17.25 |
| aster-en-12 | draft_trap | retrieval_only | 0.5000 | N/A | 17.60 |
| aster-en-13 | negative | retrieval_only | N/A | N/A | 17.79 |
| aster-en-14 | negative | retrieval_only | N/A | N/A | 18.20 |
| aster-en-15 | negative | retrieval_only | N/A | N/A | 13.92 |
| aster-en-16 | adversarial | retrieval_only | N/A | N/A | 13.19 |
| aster-en-17 | negation | retrieval_only | 1.0000 | N/A | 16.92 |
| aster-en-18 | cross_document | retrieval_only | 1.0000 | N/A | 16.03 |
| aster-zh-01 | current_version | retrieval_only | 1.0000 | N/A | 17.67 |
| aster-zh-02 | old_version | retrieval_only | 1.0000 | N/A | 17.41 |
| aster-zh-03 | similar_document | retrieval_only | 1.0000 | N/A | 17.75 |
| aster-zh-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 17.74 |
| aster-zh-05 | negation | retrieval_only | 1.0000 | N/A | 18.20 |
| aster-zh-06 | exception | retrieval_only | 1.0000 | N/A | 16.72 |
| aster-zh-07 | exception_denied | retrieval_only | 0.5000 | N/A | 16.60 |
| aster-zh-08 | negation | retrieval_only | 1.0000 | N/A | 16.19 |
| aster-zh-09 | cross_document | retrieval_only | 0.6667 | N/A | 17.54 |
| aster-zh-10 | cross_document | retrieval_only | 1.0000 | N/A | 18.31 |
| aster-zh-11 | similar_document | retrieval_only | 1.0000 | N/A | 18.40 |
| aster-zh-12 | draft_trap | retrieval_only | 0.5000 | N/A | 20.51 |
| aster-zh-13 | negative | retrieval_only | N/A | N/A | 20.40 |
| aster-zh-14 | negative | retrieval_only | N/A | N/A | 17.01 |
| aster-zh-15 | negative | retrieval_only | N/A | N/A | 16.07 |
| aster-zh-16 | adversarial | retrieval_only | N/A | N/A | 16.28 |
| aster-zh-17 | negation | retrieval_only | 1.0000 | N/A | 17.12 |
| aster-zh-18 | cross_document | retrieval_only | 0.5000 | N/A | 17.95 |
| aster-ja-01 | current_version | retrieval_only | 1.0000 | N/A | 18.13 |
| aster-ja-02 | old_version | retrieval_only | 1.0000 | N/A | 17.84 |
| aster-ja-03 | similar_document | retrieval_only | 1.0000 | N/A | 18.31 |
| aster-ja-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 18.03 |
| aster-ja-05 | negation | retrieval_only | 1.0000 | N/A | 18.94 |
| aster-ja-06 | exception | retrieval_only | 1.0000 | N/A | 17.52 |
| aster-ja-07 | exception_denied | retrieval_only | 0.5000 | N/A | 17.59 |
| aster-ja-08 | negation | retrieval_only | 1.0000 | N/A | 19.12 |
| aster-ja-09 | cross_document | retrieval_only | 0.6667 | N/A | 367.09 |
| aster-ja-10 | cross_document | retrieval_only | 1.0000 | N/A | 596.70 |
| aster-ja-11 | similar_document | retrieval_only | 1.0000 | N/A | 17.12 |
| aster-ja-12 | draft_trap | retrieval_only | 1.0000 | N/A | 19.92 |
| aster-ja-13 | negative | retrieval_only | N/A | N/A | 18.89 |
| aster-ja-14 | negative | retrieval_only | N/A | N/A | 17.50 |
| aster-ja-15 | negative | retrieval_only | N/A | N/A | 16.81 |
| aster-ja-16 | adversarial | retrieval_only | N/A | N/A | 14.29 |
| aster-ja-17 | negation | retrieval_only | 1.0000 | N/A | 20.30 |
| aster-ja-18 | cross_document | retrieval_only | 1.0000 | N/A | 18.12 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
