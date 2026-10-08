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
| query_embedding | 0.2290 | 0.2471 | 24 |
| retrieval | 3.2985 | 3.7413 | 24 |
| question_total | 9.1470 | 9.6847 | 24 |

Indexing: 29 chunks, 70.94 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| en-01 | direct | retrieval_only | 1.0000 | N/A | 10.47 |
| en-02 | direct | retrieval_only | 1.0000 | N/A | 9.36 |
| en-03 | direct | retrieval_only | 1.0000 | N/A | 9.31 |
| en-04 | direct | retrieval_only | 1.0000 | N/A | 9.53 |
| en-05 | direct | retrieval_only | 1.0000 | N/A | 9.45 |
| en-06 | direct | retrieval_only | 1.0000 | N/A | 8.39 |
| en-07 | negative | retrieval_only | N/A | N/A | 8.99 |
| en-08 | adversarial | retrieval_only | N/A | N/A | 8.67 |
| zh-01 | direct | retrieval_only | 1.0000 | N/A | 8.67 |
| zh-02 | direct | retrieval_only | 1.0000 | N/A | 9.13 |
| zh-03 | direct | retrieval_only | 1.0000 | N/A | 9.01 |
| zh-04 | direct | retrieval_only | 1.0000 | N/A | 8.79 |
| zh-05 | direct | retrieval_only | 1.0000 | N/A | 8.73 |
| zh-06 | direct | retrieval_only | 1.0000 | N/A | 8.35 |
| zh-07 | negative | insufficient_evidence | N/A | N/A | 8.22 |
| zh-08 | adversarial | retrieval_only | N/A | N/A | 8.44 |
| ja-01 | direct | retrieval_only | 1.0000 | N/A | 9.16 |
| ja-02 | direct | retrieval_only | 1.0000 | N/A | 9.22 |
| ja-03 | direct | retrieval_only | 1.0000 | N/A | 9.46 |
| ja-04 | direct | retrieval_only | 1.0000 | N/A | 8.92 |
| ja-05 | direct | retrieval_only | 1.0000 | N/A | 9.33 |
| ja-06 | direct | retrieval_only | 1.0000 | N/A | 9.71 |
| ja-07 | negative | retrieval_only | N/A | N/A | 9.30 |
| ja-08 | adversarial | retrieval_only | N/A | N/A | 9.54 |

## Limits

- Requires human review and expansion with representative held-out PDFs.
- Page text is the parser output boundary; this corpus does not measure OCR/PDF extraction.
- Test questions are held out from chunk selection but share policy topics with dev.
- Translated topics are not statistically independent samples.
