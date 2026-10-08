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
| all_claims_grounded | 0.9231 | 39 |
| answer_correctness | 0.8333 | 42 |
| citation_groundedness | 1.0000 | 36 |
| claim_groundedness | 0.9359 | 39 |
| correct_refusal | 0.9167 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.1667 | 42 |
| generator_false_refusal | 0.0952 | 42 |
| grounding_false_refusal | 0.0714 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 3 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3615 | 42 |
| refusal_accuracy | 0.8519 | 54 |
| unsupported_answer | 0.0556 | 54 |
| withheld_candidate_correctness | 1.0000 | 3 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3191.3650 | 6278.5334 | 54 |
| provider_http | 5405.0205 | 9730.8082 | 54 |
| query_embedding | 328.2060 | 441.1453 | 54 |
| retrieval | 13.1920 | 13.8969 | 54 |
| verification | 2260.5410 | 4266.9601 | 39 |
| question_total | 5426.1470 | 9751.6545 | 54 |

Indexing: 96 chunks, 19251.29 ms.
Total run API cost (USD): 0.1889. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0008; reported tokens: {'embedding_tokens': 1600, 'input_tokens': 72417, 'output_tokens': 24360, 'total_tokens': 98377, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.144998, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | answered | 1.0000 | N/A | 4623.69 |
| boreal-en-02 | old_version | answered | 1.0000 | N/A | 4947.86 |
| boreal-en-03 | similar_document | answered | 1.0000 | N/A | 5047.95 |
| boreal-en-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 2427.19 |
| boreal-en-05 | negation | answered | 1.0000 | N/A | 6395.03 |
| boreal-en-06 | exception | answered | 1.0000 | N/A | 5061.95 |
| boreal-en-07 | exception_denied | answered | 1.0000 | N/A | 7650.35 |
| boreal-en-08 | negation | answered | 1.0000 | N/A | 8258.64 |
| boreal-en-09 | cross_document | answered | 0.6667 | N/A | 7305.20 |
| boreal-en-10 | cross_document | answered | 1.0000 | N/A | 8601.47 |
| boreal-en-11 | similar_document | answered | 1.0000 | N/A | 5427.84 |
| boreal-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 8059.93 |
| boreal-en-13 | negative | insufficient_evidence | N/A | N/A | 1456.22 |
| boreal-en-14 | negative | insufficient_evidence | N/A | N/A | 1470.44 |
| boreal-en-15 | negative | answered | N/A | N/A | 4601.99 |
| boreal-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1367.49 |
| boreal-en-17 | negation | answered | 1.0000 | N/A | 6226.40 |
| boreal-en-18 | cross_document | answered | 1.0000 | N/A | 8319.39 |
| boreal-zh-01 | current_version | answered | 1.0000 | N/A | 7666.20 |
| boreal-zh-02 | old_version | answered | 1.0000 | N/A | 5294.05 |
| boreal-zh-03 | similar_document | answered | 1.0000 | N/A | 5118.10 |
| boreal-zh-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 6384.96 |
| boreal-zh-05 | negation | answered | 1.0000 | N/A | 4774.89 |
| boreal-zh-06 | exception | answered | 1.0000 | N/A | 4720.97 |
| boreal-zh-07 | exception_denied | answered | 1.0000 | N/A | 6979.88 |
| boreal-zh-08 | negation | answered | 1.0000 | N/A | 8915.96 |
| boreal-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 9582.02 |
| boreal-zh-10 | cross_document | answered | 1.0000 | N/A | 7411.92 |
| boreal-zh-11 | similar_document | answered | 1.0000 | N/A | 6786.55 |
| boreal-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 1790.70 |
| boreal-zh-13 | negative | insufficient_evidence | N/A | N/A | 2032.72 |
| boreal-zh-14 | negative | insufficient_evidence | N/A | N/A | 1631.98 |
| boreal-zh-15 | negative | insufficient_evidence | N/A | N/A | 2149.34 |
| boreal-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1374.88 |
| boreal-zh-17 | negation | answered | 1.0000 | N/A | 5403.11 |
| boreal-zh-18 | cross_document | answered | 1.0000 | N/A | 6782.75 |
| boreal-ja-01 | current_version | answered | 1.0000 | N/A | 5693.13 |
| boreal-ja-02 | old_version | unsupported_answer | 1.0000 | N/A | 4423.46 |
| boreal-ja-03 | similar_document | answered | 1.0000 | N/A | 6466.35 |
| boreal-ja-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 4052.72 |
| boreal-ja-05 | negation | answered | 1.0000 | N/A | 8245.51 |
| boreal-ja-06 | exception | answered | 1.0000 | N/A | 5069.15 |
| boreal-ja-07 | exception_denied | answered | 1.0000 | N/A | 7085.88 |
| boreal-ja-08 | negation | answered | 1.0000 | N/A | 6166.66 |
| boreal-ja-09 | cross_document | answered | 0.6667 | N/A | 11646.47 |
| boreal-ja-10 | cross_document | answered | 1.0000 | N/A | 10066.69 |
| boreal-ja-11 | similar_document | answered | 1.0000 | N/A | 6950.18 |
| boreal-ja-12 | draft_trap | answered | 1.0000 | N/A | 9423.76 |
| boreal-ja-13 | negative | insufficient_evidence | N/A | N/A | 1805.12 |
| boreal-ja-14 | negative | insufficient_evidence | N/A | N/A | 1477.63 |
| boreal-ja-15 | negative | insufficient_evidence | N/A | N/A | 1352.95 |
| boreal-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1430.73 |
| boreal-ja-17 | negation | answered | 1.0000 | N/A | 5424.46 |
| boreal-ja-18 | cross_document | answered | 0.5000 | N/A | 11338.13 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
