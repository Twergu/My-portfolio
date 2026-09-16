# RAG evaluation — policy-challenge-v2.1

Mode: **api**; split: **test**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.7857 | 42 |
| recall_at_3 | 1.0000 | 42 |
| recall_at_5 | 1.0000 | 42 |
| mrr_at_k | 0.9881 | 42 |
| ndcg_at_k | 0.9874 | 42 |
| precision_at_k | 0.2857 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | 0.9048 | 42 |
| answer_correctness | 0.9048 | 42 |
| citation_groundedness | 1.0000 | 38 |
| claim_groundedness | 0.9286 | 42 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.0952 | 42 |
| generator_false_refusal | 0.0000 | 42 |
| grounding_false_refusal | 0.0952 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 4 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3779 | 42 |
| refusal_accuracy | 0.9259 | 54 |
| unsupported_answer | 0.0741 | 54 |
| withheld_candidate_correctness | 1.0000 | 4 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 4135.8460 | 7058.1643 | 54 |
| provider_http | 13869.5435 | 19889.7725 | 54 |
| query_embedding | 335.2250 | 504.4816 | 54 |
| reranking | 6776.2435 | 11459.0501 | 54 |
| retrieval | 15.7385 | 18.0750 | 54 |
| verification | 2501.0875 | 5175.1133 | 42 |
| question_total | 13904.6206 | 19922.9541 | 54 |

Indexing: 96 chunks, 22738.28 ms.
Total run API cost (USD): 0.2790. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0020; reported tokens: {'embedding_tokens': 1600, 'input_tokens': 199565, 'output_tokens': 57980, 'total_tokens': 259145, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.169298, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | answered | 1.0000 | N/A | 15208.30 |
| boreal-en-02 | old_version | answered | 1.0000 | N/A | 13618.40 |
| boreal-en-03 | similar_document | answered | 1.0000 | N/A | 12761.81 |
| boreal-en-04 | numeric_trap | answered | 1.0000 | N/A | 14547.39 |
| boreal-en-05 | negation | unsupported_answer | 1.0000 | N/A | 15999.99 |
| boreal-en-06 | exception | answered | 1.0000 | N/A | 14708.26 |
| boreal-en-07 | exception_denied | answered | 1.0000 | N/A | 15452.45 |
| boreal-en-08 | negation | answered | 1.0000 | N/A | 14306.15 |
| boreal-en-09 | cross_document | answered | 1.0000 | N/A | 16037.09 |
| boreal-en-10 | cross_document | answered | 1.0000 | N/A | 13681.70 |
| boreal-en-11 | similar_document | answered | 1.0000 | N/A | 14594.45 |
| boreal-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 14649.63 |
| boreal-en-13 | negative | insufficient_evidence | N/A | N/A | 8645.68 |
| boreal-en-14 | negative | insufficient_evidence | N/A | N/A | 6983.66 |
| boreal-en-15 | negative | insufficient_evidence | N/A | N/A | 9243.52 |
| boreal-en-16 | adversarial | insufficient_evidence | N/A | N/A | 5122.32 |
| boreal-en-17 | negation | answered | 1.0000 | N/A | 15074.36 |
| boreal-en-18 | cross_document | answered | 1.0000 | N/A | 14267.91 |
| boreal-zh-01 | current_version | answered | 1.0000 | N/A | 12592.26 |
| boreal-zh-02 | old_version | answered | 1.0000 | N/A | 17008.90 |
| boreal-zh-03 | similar_document | answered | 1.0000 | N/A | 12351.50 |
| boreal-zh-04 | numeric_trap | answered | 1.0000 | N/A | 20842.58 |
| boreal-zh-05 | negation | answered | 1.0000 | N/A | 13967.56 |
| boreal-zh-06 | exception | answered | 1.0000 | N/A | 12613.54 |
| boreal-zh-07 | exception_denied | answered | 1.0000 | N/A | 13810.93 |
| boreal-zh-08 | negation | answered | 1.0000 | N/A | 41174.90 |
| boreal-zh-09 | cross_document | answered | 1.0000 | N/A | 14933.37 |
| boreal-zh-10 | cross_document | answered | 1.0000 | N/A | 17767.34 |
| boreal-zh-11 | similar_document | answered | 1.0000 | N/A | 16099.31 |
| boreal-zh-12 | draft_trap | answered | 1.0000 | N/A | 22663.86 |
| boreal-zh-13 | negative | insufficient_evidence | N/A | N/A | 9258.36 |
| boreal-zh-14 | negative | insufficient_evidence | N/A | N/A | 8855.60 |
| boreal-zh-15 | negative | insufficient_evidence | N/A | N/A | 8313.67 |
| boreal-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 10370.43 |
| boreal-zh-17 | negation | answered | 1.0000 | N/A | 13608.94 |
| boreal-zh-18 | cross_document | answered | 1.0000 | N/A | 12752.22 |
| boreal-ja-01 | current_version | answered | 1.0000 | N/A | 12871.65 |
| boreal-ja-02 | old_version | answered | 1.0000 | N/A | 14792.78 |
| boreal-ja-03 | similar_document | answered | 1.0000 | N/A | 13364.95 |
| boreal-ja-04 | numeric_trap | unsupported_answer | 1.0000 | N/A | 14954.94 |
| boreal-ja-05 | negation | answered | 1.0000 | N/A | 17798.87 |
| boreal-ja-06 | exception | answered | 1.0000 | N/A | 15550.50 |
| boreal-ja-07 | exception_denied | answered | 1.0000 | N/A | 15056.54 |
| boreal-ja-08 | negation | answered | 1.0000 | N/A | 15012.97 |
| boreal-ja-09 | cross_document | unsupported_answer | 1.0000 | N/A | 13841.68 |
| boreal-ja-10 | cross_document | answered | 1.0000 | N/A | 13737.84 |
| boreal-ja-11 | similar_document | answered | 1.0000 | N/A | 12725.84 |
| boreal-ja-12 | draft_trap | answered | 1.0000 | N/A | 19427.77 |
| boreal-ja-13 | negative | insufficient_evidence | N/A | N/A | 13609.64 |
| boreal-ja-14 | negative | insufficient_evidence | N/A | N/A | 10409.54 |
| boreal-ja-15 | negative | insufficient_evidence | N/A | N/A | 6823.29 |
| boreal-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 5711.42 |
| boreal-ja-17 | negation | answered | 1.0000 | N/A | 17752.84 |
| boreal-ja-18 | cross_document | answered | 1.0000 | N/A | 12534.42 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
