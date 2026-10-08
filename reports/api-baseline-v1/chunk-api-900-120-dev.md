# RAG evaluation — policy-challenge-v2.1

Mode: **api**; split: **dev**; queries: 54.

Run status: completed; requested questions: 54; indexing error: none.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_1 | 0.5992 | 42 |
| recall_at_3 | 0.8135 | 42 |
| recall_at_5 | 0.8810 | 42 |
| mrr_at_k | 0.8353 | 42 |
| ndcg_at_k | 0.8109 | 42 |
| precision_at_k | 0.2476 | 42 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | 0.7143 | 42 |
| answer_correctness | 0.6905 | 42 |
| citation_groundedness | 1.0000 | 30 |
| claim_groundedness | 0.7619 | 42 |
| correct_refusal | 0.9167 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.3095 | 42 |
| generator_false_refusal | 0.0238 | 42 |
| grounding_false_refusal | 0.2857 | 42 |
| grounding_rejected_correct_and_grounded | 0.7500 | 12 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0556 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3290 | 42 |
| refusal_accuracy | 0.7407 | 54 |
| unsupported_answer | 0.2222 | 54 |
| withheld_candidate_correctness | 1.0000 | 12 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 2573.8520 | 5026.3482 | 54 |
| provider_http | 5194.5355 | 8639.3372 | 54 |
| query_embedding | 321.7530 | 437.6913 | 54 |
| retrieval | 31.0060 | 122.8900 | 54 |
| verification | 2563.1220 | 5112.4336 | 39 |
| question_total | 5250.1360 | 8729.7730 | 54 |

Indexing: 96 chunks, 25298.37 ms.
Total run API cost (USD): 0.1626. Unknown usage or missing configured prices stay null/N/A.

Application mean USD/query: 0.0007; reported tokens: {'embedding_tokens': 1582, 'input_tokens': 64570, 'output_tokens': 18850, 'total_tokens': 85002, 'complete': True}.
Independent evaluation: {'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.126822, 'judge_errors': 0}. Judge latency and cost are excluded from application query metrics.
One pass with 2 query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 5357.81 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 5202.55 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 5116.44 |
| aster-en-04 | numeric_trap | unsupported_answer | 0.0000 | N/A | 8243.10 |
| aster-en-05 | negation | unsupported_answer | 1.0000 | N/A | 5746.73 |
| aster-en-06 | exception | answered | 1.0000 | N/A | 4776.62 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 6658.61 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 6829.91 |
| aster-en-09 | cross_document | unsupported_answer | 0.6667 | N/A | 7566.69 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 8430.65 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 4901.49 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 9153.70 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 2591.19 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1598.50 |
| aster-en-15 | negative | insufficient_evidence | N/A | N/A | 1689.34 |
| aster-en-16 | adversarial | answered | N/A | N/A | 5102.66 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 5297.72 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 7488.31 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 5385.25 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 4312.02 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 4656.05 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 8501.51 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 4166.44 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 4895.06 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 6495.98 |
| aster-zh-08 | negation | unsupported_answer | 1.0000 | N/A | 4397.05 |
| aster-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 5889.13 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 7396.95 |
| aster-zh-11 | similar_document | unsupported_answer | 1.0000 | N/A | 7457.33 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 2194.96 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 1708.90 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1746.39 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1581.75 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1845.77 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 4184.89 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 6275.61 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 6444.29 |
| aster-ja-02 | old_version | unsupported_answer | 1.0000 | N/A | 5359.54 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 4849.55 |
| aster-ja-04 | numeric_trap | unsupported_answer | 0.0000 | N/A | 3850.20 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 5148.06 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 5357.90 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 6564.93 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 6478.28 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 11425.19 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 8416.88 |
| aster-ja-11 | similar_document | unsupported_answer | 1.0000 | N/A | 7138.53 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 12590.14 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 1897.75 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1649.54 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1471.66 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1420.71 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 4788.32 |
| aster-ja-18 | cross_document | unsupported_answer | 0.5000 | N/A | 7657.00 |

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
