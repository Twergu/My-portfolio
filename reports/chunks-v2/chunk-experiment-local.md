# Chunk experiment (local)

Max dev Answer Correctness when judged, then Recall@k, nDCG@k, then fewest chunks; never test metrics.

Unicode characters, adjusted toward sentence boundaries; physical pages never merged.

| Size | Overlap | Chunks | Recall@k | Precision@k | MRR@k | nDCG@k | Correctness | Recall@1 | Recall@3 | False refusal | Index ms | Query p50 ms | Query p95 ms | USD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 450 | 0 | 100 | 0.8373 | 0.2286 | 0.7706 | 0.7419 | N/A | 0.5437 | 0.7500 | N/A | 914.9902 | 15.2112 | 15.8935 | 0.0000 |
| 450 | 60 | 100 | 0.8333 | 0.2286 | 0.7726 | 0.7415 | N/A | 0.5437 | 0.7381 | N/A | 847.9180 | 15.8043 | 16.9018 | 0.0000 |
| 900 | 0 | 96 | 0.8016 | 0.2190 | 0.7706 | 0.7237 | N/A | 0.5556 | 0.7143 | N/A | 906.8442 | 15.6788 | 18.8644 | 0.0000 |
| 900 | 120 | 96 | 0.8016 | 0.2190 | 0.7687 | 0.7227 | N/A | 0.5556 | 0.7024 | N/A | 927.1606 | 19.1874 | 56.0864 | 0.0000 |
| 1200 | 120 | 96 | 0.8016 | 0.2190 | 0.7706 | 0.7237 | N/A | 0.5556 | 0.7143 | N/A | 1179.8753 | 18.0279 | 21.0402 | 0.0000 |
| 1200 | 180 | 96 | 0.8016 | 0.2190 | 0.7706 | 0.7237 | N/A | 0.5556 | 0.7143 | N/A | 1062.6126 | 17.6794 | 20.8409 | 0.0000 |

Selected on dev: size **450**, overlap **0**.
Frozen test Recall@k: 0.8373; test nDCG@k: 0.7505.

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
