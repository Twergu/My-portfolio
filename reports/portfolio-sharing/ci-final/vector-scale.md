# pgvector Exact vs HNSW — scale benchmark

Status: **completed**; run: 2026-10-07T11:42:31.468673+00:00

Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.

| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 1.744 | 1.800 | 1.000 | measured |
| 1000 | HNSW ef=100 | 2.067 | 2.222 | 1.000 | measured |
| 1000 | HNSW ef=400 | 2.350 | 2.443 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 2.756 | 2.918 | 1.000 | measured |
| 10000 | exact | 8.327 | 9.048 | 1.000 | measured |
| 10000 | HNSW ef=100 | 2.954 | 3.165 | 0.600 | measured |
| 10000 | HNSW ef=400 | 4.893 | 5.294 | 0.920 | measured |
| 10000 | HNSW ef=1000 | 7.264 | 10.724 | 1.000 | measured |
| 100000 | exact | 79.571 | 103.004 | 1.000 | measured |
| 100000 | HNSW ef=100 | 6.764 | 7.796 | 0.160 | measured |
| 100000 | HNSW ef=400 | 18.882 | 25.253 | 0.360 | measured |
| 100000 | HNSW ef=1000 | 40.557 | 43.098 | 0.600 | measured |

Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.
