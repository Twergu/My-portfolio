# pgvector Exact vs HNSW — scale benchmark

Status: **completed**; run: 2026-09-15T01:34:32.778430+00:00

Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.

| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 3.310 | 4.268 | 1.000 | measured |
| 1000 | HNSW ef=100 | 3.994 | 4.066 | 1.000 | measured |
| 1000 | HNSW ef=400 | 4.441 | 4.542 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 5.231 | 5.342 | 1.000 | measured |
| 10000 | exact | 12.518 | 13.085 | 1.000 | measured |
| 10000 | HNSW ef=100 | 4.992 | 5.355 | 0.620 | measured |
| 10000 | HNSW ef=400 | 8.945 | 9.597 | 0.910 | measured |
| 10000 | HNSW ef=1000 | 10.344 | 11.243 | 0.990 | measured |
| 100000 | exact | 105.561 | 122.321 | 1.000 | measured |
| 100000 | HNSW ef=100 | 7.698 | 8.438 | 0.100 | measured |
| 100000 | HNSW ef=400 | 19.183 | 25.883 | 0.450 | measured |
| 100000 | HNSW ef=1000 | 38.505 | 41.492 | 0.730 | measured |

Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.
