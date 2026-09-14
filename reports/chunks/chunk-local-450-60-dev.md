# RAG evaluation — aster-synthetic-v1

Mode: **local**; split: **dev**; queries: 24.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_k | 1.0000 | 18 |
| precision_at_k | 0.2000 | 18 |
| mrr_at_k | 1.0000 | 18 |
| ndcg_at_k | 1.0000 | 18 |

Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.

| Answer metric | Mean | n |
|---|---:|---:|
| all_claims_grounded | N/A | 0 |
| claim_groundedness | N/A | 0 |
| correct_refusal | N/A | 0 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | N/A | 0 |
| reference_exact_match | N/A | 0 |
| reference_token_f1_lexical | N/A | 0 |

Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Groundedness reflects structured verifier judgments, not independent human labels.

| Latency (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| query_embedding | 0.2330 | 0.2648 | 24 |
| retrieval | 3.4870 | 4.2640 | 24 |
| question_total | 9.5118 | 10.0998 | 24 |

Indexing: 32 chunks, 71.34 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| en-01 | direct | retrieval_only | 1.0000 | N/A | 12.04 |
| en-02 | direct | retrieval_only | 1.0000 | N/A | 9.65 |
| en-03 | direct | retrieval_only | 1.0000 | N/A | 10.04 |
| en-04 | direct | retrieval_only | 1.0000 | N/A | 9.84 |
| en-05 | direct | retrieval_only | 1.0000 | N/A | 9.85 |
| en-06 | direct | retrieval_only | 1.0000 | N/A | 8.83 |
| en-07 | negative | retrieval_only | N/A | N/A | 9.45 |
| en-08 | adversarial | retrieval_only | N/A | N/A | 8.81 |
| zh-01 | direct | retrieval_only | 1.0000 | N/A | 8.87 |
| zh-02 | direct | retrieval_only | 1.0000 | N/A | 9.03 |
| zh-03 | direct | retrieval_only | 1.0000 | N/A | 8.48 |
| zh-04 | direct | retrieval_only | 1.0000 | N/A | 9.29 |
| zh-05 | direct | retrieval_only | 1.0000 | N/A | 9.57 |
| zh-06 | direct | retrieval_only | 1.0000 | N/A | 8.83 |
| zh-07 | negative | insufficient_evidence | N/A | N/A | 8.26 |
| zh-08 | adversarial | retrieval_only | N/A | N/A | 8.89 |
| ja-01 | direct | retrieval_only | 1.0000 | N/A | 9.34 |
| ja-02 | direct | retrieval_only | 1.0000 | N/A | 9.81 |
| ja-03 | direct | retrieval_only | 1.0000 | N/A | 9.77 |
| ja-04 | direct | retrieval_only | 1.0000 | N/A | 9.50 |
| ja-05 | direct | retrieval_only | 1.0000 | N/A | 9.65 |
| ja-06 | direct | retrieval_only | 1.0000 | N/A | 9.62 |
| ja-07 | negative | retrieval_only | N/A | N/A | 9.52 |
| ja-08 | adversarial | retrieval_only | N/A | N/A | 10.11 |

## Limits

- Requires human review and expansion with representative held-out PDFs.
- Page text is the parser output boundary; this corpus does not measure OCR/PDF extraction.
- Test questions are held out from chunk selection but share policy topics with dev.
- Translated topics are not statistically independent samples.
