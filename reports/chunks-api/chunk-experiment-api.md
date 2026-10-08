# Chunk experiment (api)

Max dev Answer Correctness when judged, then Recall@k, nDCG@k, then fewest chunks; never test metrics.

Unicode characters, adjusted toward sentence boundaries; physical pages never merged.

| Size | Overlap | Chunks | Recall@k | Precision@k | MRR@k | nDCG@k | Correctness | Recall@1 | Recall@3 | False refusal | Index ms | Query p50 ms | Query p95 ms | USD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 450 | 0 | 100 | 0.9048 | 0.2524 | 0.8373 | 0.8177 | 0.7857 | 0.5992 | 0.8056 | 0.2143 | 19682.6875 | 6866.2266 | 11097.6768 | 0.2031 |
| 450 | 60 | 100 | 0.9048 | 0.2524 | 0.8254 | 0.8123 | 0.7619 | 0.5873 | 0.8056 | 0.2381 | 16635.5666 | 5991.3406 | 10409.0792 | 0.1879 |
| 900 | 0 | 96 | 0.8810 | 0.2476 | 0.8353 | 0.8128 | 0.8571 | 0.5992 | 0.8135 | 0.1429 | 24288.3310 | 5988.0166 | 11451.9354 | 0.1943 |
| 900 | 120 | 96 | 0.8810 | 0.2476 | 0.8353 | 0.8128 | 0.8333 | 0.5992 | 0.8135 | 0.1429 | 22949.6191 | 5800.8790 | 11267.2034 | 0.1902 |
| 1200 | 120 | 96 | 0.8810 | 0.2476 | 0.8234 | 0.8074 | 0.7619 | 0.5873 | 0.8135 | 0.1905 | 18023.4252 | 5839.2333 | 11028.4860 | 0.1890 |
| 1200 | 180 | 96 | 0.8810 | 0.2476 | 0.8353 | 0.8109 | 0.7857 | 0.5992 | 0.8135 | 0.2143 | 20143.2760 | 5737.8147 | 12018.5834 | 0.1958 |

Selected on dev: size **900**, overlap **0**.
Frozen test Recall@k: 0.8810; test nDCG@k: 0.8055.

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
