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
| query_embedding | 0.2465 | 0.2823 | 24 |
| retrieval | 3.1200 | 3.9899 | 24 |
| question_total | 9.6474 | 11.0968 | 24 |

Indexing: 17 chunks, 65.30 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| en-01 | direct | retrieval_only | 1.0000 | N/A | 9.79 |
| en-02 | direct | retrieval_only | 1.0000 | N/A | 8.77 |
| en-03 | direct | retrieval_only | 1.0000 | N/A | 9.05 |
| en-04 | direct | retrieval_only | 1.0000 | N/A | 11.01 |
| en-05 | direct | retrieval_only | 1.0000 | N/A | 9.88 |
| en-06 | direct | retrieval_only | 1.0000 | N/A | 8.96 |
| en-07 | negative | retrieval_only | N/A | N/A | 9.65 |
| en-08 | adversarial | retrieval_only | N/A | N/A | 9.82 |
| zh-01 | direct | retrieval_only | 1.0000 | N/A | 9.98 |
| zh-02 | direct | retrieval_only | 1.0000 | N/A | 9.62 |
| zh-03 | direct | retrieval_only | 1.0000 | N/A | 10.32 |
| zh-04 | direct | retrieval_only | 1.0000 | N/A | 10.72 |
| zh-05 | direct | retrieval_only | 1.0000 | N/A | 11.11 |
| zh-06 | direct | retrieval_only | 1.0000 | N/A | 194.40 |
| zh-07 | negative | insufficient_evidence | N/A | N/A | 9.11 |
| zh-08 | adversarial | retrieval_only | N/A | N/A | 9.48 |
| ja-01 | direct | retrieval_only | 1.0000 | N/A | 9.75 |
| ja-02 | direct | retrieval_only | 1.0000 | N/A | 9.65 |
| ja-03 | direct | retrieval_only | 1.0000 | N/A | 9.26 |
| ja-04 | direct | retrieval_only | 1.0000 | N/A | 9.20 |
| ja-05 | direct | retrieval_only | 1.0000 | N/A | 8.96 |
| ja-06 | direct | retrieval_only | 1.0000 | N/A | 8.94 |
| ja-07 | negative | retrieval_only | N/A | N/A | 9.64 |
| ja-08 | adversarial | retrieval_only | N/A | N/A | 9.45 |

## Limits

- Requires human review and expansion with representative held-out PDFs.
- Page text is the parser output boundary; this corpus does not measure OCR/PDF extraction.
- Test questions are held out from chunk selection but share policy topics with dev.
- Translated topics are not statistically independent samples.
