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
| query_embedding | 0.2370 | 0.2545 | 24 |
| retrieval | 2.9990 | 3.3914 | 24 |
| question_total | 8.9483 | 9.9018 | 24 |

Indexing: 17 chunks, 63.40 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| en-01 | direct | retrieval_only | 1.0000 | N/A | 9.94 |
| en-02 | direct | retrieval_only | 1.0000 | N/A | 8.81 |
| en-03 | direct | retrieval_only | 1.0000 | N/A | 9.07 |
| en-04 | direct | retrieval_only | 1.0000 | N/A | 9.00 |
| en-05 | direct | retrieval_only | 1.0000 | N/A | 9.30 |
| en-06 | direct | retrieval_only | 1.0000 | N/A | 8.06 |
| en-07 | negative | retrieval_only | N/A | N/A | 9.28 |
| en-08 | adversarial | retrieval_only | N/A | N/A | 8.41 |
| zh-01 | direct | retrieval_only | 1.0000 | N/A | 8.66 |
| zh-02 | direct | retrieval_only | 1.0000 | N/A | 9.05 |
| zh-03 | direct | retrieval_only | 1.0000 | N/A | 9.25 |
| zh-04 | direct | retrieval_only | 1.0000 | N/A | 10.25 |
| zh-05 | direct | retrieval_only | 1.0000 | N/A | 8.75 |
| zh-06 | direct | retrieval_only | 1.0000 | N/A | 8.64 |
| zh-07 | negative | insufficient_evidence | N/A | N/A | 8.21 |
| zh-08 | adversarial | retrieval_only | N/A | N/A | 8.87 |
| ja-01 | direct | retrieval_only | 1.0000 | N/A | 8.87 |
| ja-02 | direct | retrieval_only | 1.0000 | N/A | 9.19 |
| ja-03 | direct | retrieval_only | 1.0000 | N/A | 8.95 |
| ja-04 | direct | retrieval_only | 1.0000 | N/A | 8.96 |
| ja-05 | direct | retrieval_only | 1.0000 | N/A | 8.92 |
| ja-06 | direct | retrieval_only | 1.0000 | N/A | 9.69 |
| ja-07 | negative | retrieval_only | N/A | N/A | 8.79 |
| ja-08 | adversarial | retrieval_only | N/A | N/A | 8.95 |

## Limits

- Requires human review and expansion with representative held-out PDFs.
- Page text is the parser output boundary; this corpus does not measure OCR/PDF extraction.
- Test questions are held out from chunk selection but share policy topics with dev.
- Translated topics are not statistically independent samples.
