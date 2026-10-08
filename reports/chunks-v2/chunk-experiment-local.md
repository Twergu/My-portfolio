# Chunk experiment (local)

Max dev Answer Correctness when judged, then Recall@k, nDCG@k, then fewest chunks; never test metrics.

Unicode characters, adjusted toward sentence boundaries; physical pages never merged.

| Size | Overlap | Chunks | Recall@k | Precision@k | MRR@k | nDCG@k | Correctness | Recall@1 | Recall@3 | False refusal | Index ms | Query p50 ms | Query p95 ms | USD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 450 | 0 | 100 | 0.8690 | 0.2429 | 0.8004 | 0.7713 | N/A | 0.5675 | 0.7262 | N/A | 1520.8525 | 23.8827 | 27.0414 | 0.0000 |
| 450 | 60 | 100 | 0.8611 | 0.2381 | 0.8123 | 0.7717 | N/A | 0.5794 | 0.7262 | N/A | 1247.7121 | 23.6963 | 30.7494 | 0.0000 |
| 900 | 0 | 96 | 0.8254 | 0.2286 | 0.8004 | 0.7511 | N/A | 0.5794 | 0.7024 | N/A | 2150.8691 | 22.3122 | 28.2383 | 0.0000 |
| 900 | 120 | 96 | 0.8254 | 0.2286 | 0.8004 | 0.7511 | N/A | 0.5794 | 0.7024 | N/A | 1214.8444 | 21.9775 | 26.9728 | 0.0000 |
| 1200 | 120 | 96 | 0.8254 | 0.2286 | 0.8004 | 0.7511 | N/A | 0.5794 | 0.7024 | N/A | 1979.6608 | 24.4888 | 32.7254 | 0.0000 |
| 1200 | 180 | 96 | 0.8254 | 0.2286 | 0.8004 | 0.7511 | N/A | 0.5794 | 0.7024 | N/A | 1120.3461 | 20.3105 | 23.5908 | 0.0000 |

Selected on dev: size **450**, overlap **0**.
Frozen test Recall@k: 0.8611; test nDCG@k: 0.7819.

The test split did not participate in parameter selection. Existing production defaults were not changed.

## Limits

- Templated multilingual cases are correlated, not independent statistical samples.
- Dev/test use different organizations and numbers but share rule templates.
- Reference evidence is page-level; retrieval recall does not establish fact coverage.
- Human review on representative private documents remains necessary.
- Page text starts after PDF parsing; end-to-end PDF coverage is tested by live_smoke.
- One pass on a tiny corpus; p95 is descriptive, not a statistically stable production estimate.
- Local hashed retrieval is a baseline, not a multilingual embedding model.
- Changing production defaults is a separate decision; this script only reports results.
