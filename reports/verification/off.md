# RAG evaluation — policy-challenge-v2.1

Mode: **api**; split: **test**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5833 | 42 |
| recall_at_3 | 0.8452 | 42 |
| recall_at_5 | 0.8810 | 42 |
| mrr_at_k | 0.8254 | 42 |
| ndcg_at_k | 0.8055 | 42 |
| precision_at_k | 0.2476 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | N/A | 0 |
| answer_correctness | 0.9762 | 42 |
| citation_groundedness | 1.0000 | 41 |
| claim_groundedness | N/A | 0 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.0238 | 42 |
| generator_false_refusal | 0.0238 | 42 |
| grounding_false_refusal | 0.0000 | 42 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.4097 | 42 |
| refusal_accuracy | 0.9815 | 54 |
| unsupported_answer | 0.0000 | 54 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3160.4220 | 6520.8744 | 54 |
| provider_http | 3506.8535 | 6802.2297 | 54 |
| query_embedding | 309.2435 | 422.3744 | 54 |
| retrieval | 12.6505 | 13.8556 | 54 |
| question_total | 3527.5054 | 6822.6271 | 54 |

Indexing: 96 chunks, 18573.85 ms.
Total run API cost (USD): 0.1873. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0006; reported tokens: {'embedding_tokens': 1600, 'input_tokens': 51133, 'output_tokens': 17128, 'total_tokens': 69861, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.156276, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | answered | 1.0000 | N/A | 4682.73 |
| boreal-en-02 | old_version | answered | 1.0000 | N/A | 2451.05 |
| boreal-en-03 | similar_document | answered | 1.0000 | N/A | 3576.47 |
| boreal-en-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 6387.92 |
| boreal-en-05 | negation | answered | 1.0000 | N/A | 6580.75 |
| boreal-en-06 | exception | answered | 1.0000 | N/A | 2987.20 |
| boreal-en-07 | exception_denied | answered | 1.0000 | N/A | 3364.26 |
| boreal-en-08 | negation | answered | 1.0000 | N/A | 3591.09 |
| boreal-en-09 | cross_document | answered | 0.6667 | N/A | 3991.16 |
| boreal-en-10 | cross_document | answered | 1.0000 | N/A | 5818.42 |
| boreal-en-11 | similar_document | answered | 1.0000 | N/A | 2660.73 |
| boreal-en-12 | draft_trap | answered | 1.0000 | N/A | 3812.10 |
| boreal-en-13 | negative | insufficient_evidence | N/A | N/A | 1770.33 |
| boreal-en-14 | negative | insufficient_evidence | N/A | N/A | 1398.21 |
| boreal-en-15 | negative | insufficient_evidence | N/A | N/A | 1739.26 |
| boreal-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1342.41 |
| boreal-en-17 | negation | answered | 1.0000 | N/A | 3296.45 |
| boreal-en-18 | cross_document | answered | 1.0000 | N/A | 4866.27 |
| boreal-zh-01 | current_version | answered | 1.0000 | N/A | 3439.58 |
| boreal-zh-02 | old_version | answered | 1.0000 | N/A | 2840.57 |
| boreal-zh-03 | similar_document | answered | 1.0000 | N/A | 3419.26 |
| boreal-zh-04 | numeric_trap | answered | 0.0000 | N/A | 6654.49 |
| boreal-zh-05 | negation | answered | 1.0000 | N/A | 3090.74 |
| boreal-zh-06 | exception | answered | 1.0000 | N/A | 3261.49 |
| boreal-zh-07 | exception_denied | answered | 1.0000 | N/A | 4973.70 |
| boreal-zh-08 | negation | answered | 1.0000 | N/A | 5135.40 |
| boreal-zh-09 | cross_document | answered | 0.6667 | N/A | 2996.01 |
| boreal-zh-10 | cross_document | answered | 1.0000 | N/A | 5401.79 |
| boreal-zh-11 | similar_document | answered | 1.0000 | N/A | 3916.84 |
| boreal-zh-12 | draft_trap | answered | 0.5000 | N/A | 4890.84 |
| boreal-zh-13 | negative | insufficient_evidence | N/A | N/A | 2041.90 |
| boreal-zh-14 | negative | insufficient_evidence | N/A | N/A | 1622.09 |
| boreal-zh-15 | negative | insufficient_evidence | N/A | N/A | 1470.39 |
| boreal-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1856.16 |
| boreal-zh-17 | negation | answered | 1.0000 | N/A | 2420.54 |
| boreal-zh-18 | cross_document | answered | 1.0000 | N/A | 4582.45 |
| boreal-ja-01 | current_version | answered | 1.0000 | N/A | 3805.51 |
| boreal-ja-02 | old_version | answered | 1.0000 | N/A | 3424.46 |
| boreal-ja-03 | similar_document | answered | 1.0000 | N/A | 2917.03 |
| boreal-ja-04 | numeric_trap | answered | 0.0000 | N/A | 7134.87 |
| boreal-ja-05 | negation | answered | 1.0000 | N/A | 5450.55 |
| boreal-ja-06 | exception | answered | 1.0000 | N/A | 5271.49 |
| boreal-ja-07 | exception_denied | answered | 1.0000 | N/A | 3708.91 |
| boreal-ja-08 | negation | answered | 1.0000 | N/A | 3478.54 |
| boreal-ja-09 | cross_document | answered | 0.6667 | N/A | 4589.99 |
| boreal-ja-10 | cross_document | answered | 1.0000 | N/A | 4349.82 |
| boreal-ja-11 | similar_document | answered | 1.0000 | N/A | 4180.82 |
| boreal-ja-12 | draft_trap | answered | 1.0000 | N/A | 4950.11 |
| boreal-ja-13 | negative | insufficient_evidence | N/A | N/A | 1820.34 |
| boreal-ja-14 | negative | insufficient_evidence | N/A | N/A | 1400.30 |
| boreal-ja-15 | negative | insufficient_evidence | N/A | N/A | 1217.22 |
| boreal-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1288.59 |
| boreal-ja-17 | negation | answered | 1.0000 | N/A | 7270.58 |
| boreal-ja-18 | cross_document | answered | 0.5000 | N/A | 7244.55 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
