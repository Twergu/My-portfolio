# RAG evaluation — policy-challenge-v2.1

Mode: **api**; split: **test**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.7619 | 42 |
| recall_at_3 | 1.0000 | 42 |
| recall_at_5 | 1.0000 | 42 |
| mrr_at_k | 0.9762 | 42 |
| ndcg_at_k | 0.9805 | 42 |
| precision_at_k | 0.2857 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | N/A | 0 |
| answer_correctness | 0.9286 | 42 |
| citation_groundedness | 1.0000 | 40 |
| claim_groundedness | N/A | 0 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.0476 | 42 |
| generator_false_refusal | 0.0476 | 42 |
| grounding_false_refusal | 0.0000 | 42 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3701 | 42 |
| refusal_accuracy | 0.9630 | 54 |
| unsupported_answer | 0.0000 | 54 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3784.6145 | 7452.1552 | 54 |
| provider_http | 10470.6820 | 15261.4588 | 54 |
| query_embedding | 341.3315 | 630.1935 | 54 |
| reranking | 6494.5820 | 9922.3820 | 54 |
| retrieval | 15.1610 | 23.1396 | 54 |
| question_total | 10497.5124 | 15314.5513 | 54 |

Indexing: 96 chunks, 23241.44 ms.
Total run API cost (USD): 0.2510. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0017; reported tokens: {'embedding_tokens': 1600, 'input_tokens': 174332, 'output_tokens': 47126, 'total_tokens': 223058, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.159398, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | answered | 1.0000 | N/A | 8632.73 |
| boreal-en-02 | old_version | answered | 1.0000 | N/A | 10239.25 |
| boreal-en-03 | similar_document | answered | 1.0000 | N/A | 9014.48 |
| boreal-en-04 | numeric_trap | answered | 1.0000 | N/A | 10720.41 |
| boreal-en-05 | negation | answered | 1.0000 | N/A | 10305.47 |
| boreal-en-06 | exception | answered | 1.0000 | N/A | 10352.31 |
| boreal-en-07 | exception_denied | answered | 1.0000 | N/A | 10886.22 |
| boreal-en-08 | negation | answered | 1.0000 | N/A | 7308.61 |
| boreal-en-09 | cross_document | answered | 1.0000 | N/A | 12869.08 |
| boreal-en-10 | cross_document | answered | 1.0000 | N/A | 12008.22 |
| boreal-en-11 | similar_document | answered | 1.0000 | N/A | 10250.88 |
| boreal-en-12 | draft_trap | answered | 1.0000 | N/A | 9910.11 |
| boreal-en-13 | negative | insufficient_evidence | N/A | N/A | 8361.76 |
| boreal-en-14 | negative | insufficient_evidence | N/A | N/A | 8124.00 |
| boreal-en-15 | negative | insufficient_evidence | N/A | N/A | 7304.34 |
| boreal-en-16 | adversarial | insufficient_evidence | N/A | N/A | 7518.93 |
| boreal-en-17 | negation | answered | 1.0000 | N/A | 14366.98 |
| boreal-en-18 | cross_document | answered | 1.0000 | N/A | 12941.35 |
| boreal-zh-01 | current_version | answered | 1.0000 | N/A | 8087.88 |
| boreal-zh-02 | old_version | answered | 1.0000 | N/A | 11767.11 |
| boreal-zh-03 | similar_document | answered | 1.0000 | N/A | 10320.58 |
| boreal-zh-04 | numeric_trap | answered | 1.0000 | N/A | 16443.35 |
| boreal-zh-05 | negation | insufficient_evidence | 1.0000 | N/A | 11961.26 |
| boreal-zh-06 | exception | answered | 1.0000 | N/A | 8606.47 |
| boreal-zh-07 | exception_denied | answered | 1.0000 | N/A | 11679.91 |
| boreal-zh-08 | negation | answered | 1.0000 | N/A | 11859.16 |
| boreal-zh-09 | cross_document | answered | 1.0000 | N/A | 11287.88 |
| boreal-zh-10 | cross_document | answered | 1.0000 | N/A | 10582.99 |
| boreal-zh-11 | similar_document | answered | 1.0000 | N/A | 10696.45 |
| boreal-zh-12 | draft_trap | answered | 1.0000 | N/A | 11170.20 |
| boreal-zh-13 | negative | insufficient_evidence | N/A | N/A | 8468.11 |
| boreal-zh-14 | negative | insufficient_evidence | N/A | N/A | 8120.10 |
| boreal-zh-15 | negative | insufficient_evidence | N/A | N/A | 11268.58 |
| boreal-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 6074.02 |
| boreal-zh-17 | negation | answered | 1.0000 | N/A | 10207.33 |
| boreal-zh-18 | cross_document | answered | 1.0000 | N/A | 11093.19 |
| boreal-ja-01 | current_version | answered | 1.0000 | N/A | 13149.68 |
| boreal-ja-02 | old_version | answered | 1.0000 | N/A | 9019.37 |
| boreal-ja-03 | similar_document | answered | 1.0000 | N/A | 8286.75 |
| boreal-ja-04 | numeric_trap | insufficient_evidence | 1.0000 | N/A | 11582.89 |
| boreal-ja-05 | negation | answered | 1.0000 | N/A | 12063.43 |
| boreal-ja-06 | exception | answered | 1.0000 | N/A | 8104.05 |
| boreal-ja-07 | exception_denied | answered | 1.0000 | N/A | 10412.04 |
| boreal-ja-08 | negation | answered | 1.0000 | N/A | 16955.56 |
| boreal-ja-09 | cross_document | answered | 1.0000 | N/A | 14445.87 |
| boreal-ja-10 | cross_document | answered | 1.0000 | N/A | 15806.01 |
| boreal-ja-11 | similar_document | answered | 1.0000 | N/A | 10797.21 |
| boreal-ja-12 | draft_trap | answered | 1.0000 | N/A | 15049.92 |
| boreal-ja-13 | negative | insufficient_evidence | N/A | N/A | 8873.96 |
| boreal-ja-14 | negative | insufficient_evidence | N/A | N/A | 12126.44 |
| boreal-ja-15 | negative | insufficient_evidence | N/A | N/A | 7961.51 |
| boreal-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 9104.75 |
| boreal-ja-17 | negation | answered | 1.0000 | N/A | 9106.82 |
| boreal-ja-18 | cross_document | answered | 1.0000 | N/A | 11670.40 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
