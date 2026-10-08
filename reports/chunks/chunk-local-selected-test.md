# RAG evaluation — aster-synthetic-v1

Mode: **local**; split: **test**; queries: 12.

Synthetic seed only. Test results are not evidence of production accuracy.

| Retrieval metric (macro, answerable only) | Mean | n |
|---|---:|---:|
| recall_at_k | 1.0000 | 9 |
| precision_at_k | 0.2667 | 9 |
| mrr_at_k | 0.8056 | 9 |
| ndcg_at_k | 0.8547 | 9 |

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
| query_embedding | 0.2365 | 0.2779 | 12 |
| retrieval | 3.0605 | 3.3813 | 12 |
| question_total | 9.3126 | 9.9711 | 12 |

Indexing: 17 chunks, 65.09 ms.
Total run API cost (USD): 0.0000. Unknown usage or missing configured prices stay null/N/A.

One sequential pass; no warmup or concurrency. Timings are measured, not estimates.

## Per question

| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |
|---|---|---|---:|---:|---:|
| en-09 | direct | retrieval_only | 1.0000 | N/A | 10.21 |
| en-10 | cross_page | retrieval_only | 1.0000 | N/A | 9.21 |
| en-11 | negative | retrieval_only | N/A | N/A | 9.37 |
| en-12 | adversarial | retrieval_only | 1.0000 | N/A | 9.09 |
| zh-09 | direct | retrieval_only | 1.0000 | N/A | 9.54 |
| zh-10 | cross_page | retrieval_only | 1.0000 | N/A | 9.19 |
| zh-11 | negative | retrieval_only | N/A | N/A | 9.18 |
| zh-12 | adversarial | retrieval_only | 1.0000 | N/A | 9.25 |
| ja-09 | direct | retrieval_only | 1.0000 | N/A | 9.69 |
| ja-10 | cross_page | retrieval_only | 1.0000 | N/A | 9.78 |
| ja-11 | negative | retrieval_only | N/A | N/A | 8.96 |
| ja-12 | adversarial | retrieval_only | 1.0000 | N/A | 9.38 |

## Limits

- Requires human review and expansion with representative held-out PDFs.
- Page text is the parser output boundary; this corpus does not measure OCR/PDF extraction.
- Test questions are held out from chunk selection but share policy topics with dev.
- Translated topics are not statistically independent samples.
