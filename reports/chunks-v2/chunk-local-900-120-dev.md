# RAG evaluation — policy-challenge-v2.1

Mode: **local**; split: **dev**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5794 | 42 |
| recall_at_3 | 0.6905 | 42 |
| recall_at_5 | 0.8254 | 42 |
| mrr_at_k | 0.8004 | 42 |
| ndcg_at_k | 0.7500 | 42 |
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
| query_embedding | 0.3505 | 0.6137 | 54 |
| retrieval | 12.3450 | 16.3273 | 54 |
| question_total | 21.2691 | 28.3130 | 54 |

Indexing: 96 chunks, 1203.45 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0000; reported tokens: {'embedding_tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'not_applicable', 'judge_cost_usd': 0.0, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | retrieval_only | 0.0000 | N/A | 22.29 |
| aster-en-02 | old_version | retrieval_only | 1.0000 | N/A | 19.27 |
| aster-en-03 | similar_document | retrieval_only | 1.0000 | N/A | 20.08 |
| aster-en-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 21.32 |
| aster-en-05 | negation | retrieval_only | 1.0000 | N/A | 18.99 |
| aster-en-06 | exception | retrieval_only | 1.0000 | N/A | 21.49 |
| aster-en-07 | exception_denied | retrieval_only | 0.5000 | N/A | 20.33 |
| aster-en-08 | negation | retrieval_only | 1.0000 | N/A | 20.62 |
| aster-en-09 | cross_document | retrieval_only | 0.3333 | N/A | 21.18 |
| aster-en-10 | cross_document | retrieval_only | 1.0000 | N/A | 22.27 |
| aster-en-11 | similar_document | retrieval_only | 1.0000 | N/A | 23.28 |
| aster-en-12 | draft_trap | retrieval_only | 0.5000 | N/A | 24.30 |
| aster-en-13 | negative | retrieval_only | N/A | N/A | 23.36 |
| aster-en-14 | negative | retrieval_only | N/A | N/A | 22.10 |
| aster-en-15 | negative | retrieval_only | N/A | N/A | 475.01 |
| aster-en-16 | adversarial | retrieval_only | N/A | N/A | 336.65 |
| aster-en-17 | negation | retrieval_only | 1.0000 | N/A | 24.56 |
| aster-en-18 | cross_document | retrieval_only | 1.0000 | N/A | 24.20 |
| aster-zh-01 | current_version | retrieval_only | 1.0000 | N/A | 25.18 |
| aster-zh-02 | old_version | retrieval_only | 1.0000 | N/A | 27.95 |
| aster-zh-03 | similar_document | retrieval_only | 1.0000 | N/A | 22.36 |
| aster-zh-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 20.27 |
| aster-zh-05 | negation | retrieval_only | 1.0000 | N/A | 20.54 |
| aster-zh-06 | exception | retrieval_only | 1.0000 | N/A | 19.85 |
| aster-zh-07 | exception_denied | retrieval_only | 1.0000 | N/A | 19.38 |
| aster-zh-08 | negation | retrieval_only | 1.0000 | N/A | 19.04 |
| aster-zh-09 | cross_document | retrieval_only | 0.6667 | N/A | 21.59 |
| aster-zh-10 | cross_document | retrieval_only | 1.0000 | N/A | 20.95 |
| aster-zh-11 | similar_document | retrieval_only | 1.0000 | N/A | 21.34 |
| aster-zh-12 | draft_trap | retrieval_only | 0.5000 | N/A | 20.47 |
| aster-zh-13 | negative | retrieval_only | N/A | N/A | 21.39 |
| aster-zh-14 | negative | retrieval_only | N/A | N/A | 20.70 |
| aster-zh-15 | negative | retrieval_only | N/A | N/A | 15.92 |
| aster-zh-16 | adversarial | retrieval_only | N/A | N/A | 17.93 |
| aster-zh-17 | negation | retrieval_only | 1.0000 | N/A | 25.59 |
| aster-zh-18 | cross_document | retrieval_only | 1.0000 | N/A | 24.73 |
| aster-ja-01 | current_version | retrieval_only | 1.0000 | N/A | 21.86 |
| aster-ja-02 | old_version | retrieval_only | 1.0000 | N/A | 21.37 |
| aster-ja-03 | similar_document | retrieval_only | 1.0000 | N/A | 19.89 |
| aster-ja-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 21.22 |
| aster-ja-05 | negation | retrieval_only | 1.0000 | N/A | 20.97 |
| aster-ja-06 | exception | retrieval_only | 1.0000 | N/A | 21.12 |
| aster-ja-07 | exception_denied | retrieval_only | 0.5000 | N/A | 19.92 |
| aster-ja-08 | negation | retrieval_only | 1.0000 | N/A | 20.22 |
| aster-ja-09 | cross_document | retrieval_only | 0.6667 | N/A | 19.40 |
| aster-ja-10 | cross_document | retrieval_only | 1.0000 | N/A | 19.82 |
| aster-ja-11 | similar_document | retrieval_only | 1.0000 | N/A | 20.53 |
| aster-ja-12 | draft_trap | retrieval_only | 1.0000 | N/A | 20.26 |
| aster-ja-13 | negative | retrieval_only | N/A | N/A | 28.38 |
| aster-ja-14 | negative | retrieval_only | N/A | N/A | 26.38 |
| aster-ja-15 | negative | retrieval_only | N/A | N/A | 23.15 |
| aster-ja-16 | adversarial | retrieval_only | N/A | N/A | 21.02 |
| aster-ja-17 | negation | retrieval_only | 1.0000 | N/A | 28.28 |
| aster-ja-18 | cross_document | retrieval_only | 1.0000 | N/A | 23.11 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
