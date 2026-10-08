# Chunk experiment (local)

Max dev Recall@k, then dev nDCG@k, then fewest chunks; never test metrics.

Unicode characters, adjusted toward sentence boundaries; physical pages never merged.

| Size | Overlap | Chunks | Recall@k | Precision@k | MRR@k | nDCG@k | Index ms | Query p50 ms | Query p95 ms | USD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 450 | 0 | 29 | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 70.9418 | 9.1470 | 9.6847 | 0.0000 |
| 450 | 60 | 32 | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 71.3438 | 9.5118 | 10.0998 | 0.0000 |
| 900 | 0 | 19 | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 64.6143 | 8.8728 | 9.2739 | 0.0000 |
| 900 | 120 | 19 | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 64.4755 | 9.0175 | 9.6732 | 0.0000 |
| 1200 | 120 | 17 | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 65.3001 | 9.6474 | 11.0968 | 0.0000 |
| 1200 | 180 | 17 | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 63.4022 | 8.9483 | 9.9018 | 0.0000 |

Selected on dev: size **1200**, overlap **120**.
Frozen test Recall@k: 1.0000; test nDCG@k: 0.8547.

The test split did not participate in parameter selection. Existing production defaults were not changed.

## Limits

- Requires human review and expansion with representative held-out PDFs.
- Page text is the parser output boundary; this corpus does not measure OCR/PDF extraction.
- Test questions are held out from chunk selection but share policy topics with dev.
- Translated topics are not statistically independent samples.
- One pass on a tiny corpus; p95 is descriptive, not a statistically stable production estimate.
- Local hashed retrieval is a baseline, not a multilingual embedding model.
- Changing production defaults is a separate decision; this script only reports results.
