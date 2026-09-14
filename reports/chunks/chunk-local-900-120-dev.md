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
| query_embedding | 0.2310 | 0.2428 | 24 |
| retrieval | 2.9945 | 3.5837 | 24 |
| question_total | 9.0175 | 9.6732 | 24 |

Indexing: 19 chunks, 64.48 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| en-01 | direct | retrieval_only | 1.0000 | N/A | 10.22 |
| en-02 | direct | retrieval_only | 1.0000 | N/A | 9.14 |
| en-03 | direct | retrieval_only | 1.0000 | N/A | 9.29 |
| en-04 | direct | retrieval_only | 1.0000 | N/A | 9.43 |
| en-05 | direct | retrieval_only | 1.0000 | N/A | 9.33 |
| en-06 | direct | retrieval_only | 1.0000 | N/A | 8.61 |
| en-07 | negative | retrieval_only | N/A | N/A | 9.17 |
| en-08 | adversarial | retrieval_only | N/A | N/A | 8.71 |
| zh-01 | direct | retrieval_only | 1.0000 | N/A | 8.97 |
| zh-02 | direct | retrieval_only | 1.0000 | N/A | 9.07 |
| zh-03 | direct | retrieval_only | 1.0000 | N/A | 8.68 |
| zh-04 | direct | retrieval_only | 1.0000 | N/A | 9.12 |
| zh-05 | direct | retrieval_only | 1.0000 | N/A | 8.68 |
| zh-06 | direct | retrieval_only | 1.0000 | N/A | 8.38 |
| zh-07 | negative | insufficient_evidence | N/A | N/A | 8.20 |
| zh-08 | adversarial | retrieval_only | N/A | N/A | 8.72 |
| ja-01 | direct | retrieval_only | 1.0000 | N/A | 9.30 |
| ja-02 | direct | retrieval_only | 1.0000 | N/A | 9.07 |
| ja-03 | direct | retrieval_only | 1.0000 | N/A | 8.75 |
| ja-04 | direct | retrieval_only | 1.0000 | N/A | 8.92 |
| ja-05 | direct | retrieval_only | 1.0000 | N/A | 9.72 |
| ja-06 | direct | retrieval_only | 1.0000 | N/A | 8.83 |
| ja-07 | negative | retrieval_only | N/A | N/A | 8.94 |
| ja-08 | adversarial | retrieval_only | N/A | N/A | 9.17 |

## Limits

- Requires human review and expansion with representative held-out PDFs.
- Page text is the parser output boundary; this corpus does not measure OCR/PDF extraction.
- Test questions are held out from chunk selection but share policy topics with dev.
- Translated topics are not statistically independent samples.
