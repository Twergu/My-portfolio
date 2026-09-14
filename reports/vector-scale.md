# pgvector Exact vs HNSW — scale benchmark

Status: **completed**; run: 2026-09-14T09:39:59.592400+00:00

Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.

| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 2.359 | 2.480 | 1.000 | measured |
| 1000 | HNSW ef=100 | 2.705 | 3.200 | 1.000 | measured |
| 1000 | HNSW ef=400 | 3.027 | 3.163 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 3.635 | 3.765 | 1.000 | measured |
| 10000 | exact | 8.452 | 8.919 | 1.000 | measured |
| 10000 | HNSW ef=100 | 3.471 | 3.636 | 0.600 | measured |
| 10000 | HNSW ef=400 | 5.491 | 6.874 | 0.900 | measured |
| 10000 | HNSW ef=1000 | 7.486 | 9.042 | 1.000 | measured |
| 100000 | exact | 90.353 | 93.435 | 1.000 | measured |
| 100000 | HNSW ef=100 | 6.611 | 7.372 | 0.170 | measured |
| 100000 | HNSW ef=400 | 15.915 | 19.596 | 0.350 | measured |
| 100000 | HNSW ef=1000 | 34.105 | 36.235 | 0.590 | measured |

Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.
