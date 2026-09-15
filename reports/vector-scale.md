# pgvector Exact vs HNSW — scale benchmark

Status: **completed**; run: 2026-09-14T11:05:47.729065+00:00

Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.

| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 3.262 | 3.775 | 1.000 | measured |
| 1000 | HNSW ef=100 | 3.891 | 3.985 | 1.000 | measured |
| 1000 | HNSW ef=400 | 4.306 | 4.373 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 5.071 | 5.260 | 1.000 | measured |
| 10000 | exact | 12.782 | 19.718 | 1.000 | measured |
| 10000 | HNSW ef=100 | 4.920 | 5.117 | 0.590 | measured |
| 10000 | HNSW ef=400 | 7.234 | 9.697 | 0.980 | measured |
| 10000 | HNSW ef=1000 | 9.326 | 10.011 | 1.000 | measured |
| 100000 | exact | 106.170 | 121.557 | 1.000 | measured |
| 100000 | HNSW ef=100 | 7.941 | 8.915 | 0.110 | measured |
| 100000 | HNSW ef=400 | 18.927 | 27.118 | 0.380 | measured |
| 100000 | HNSW ef=1000 | 38.935 | 42.164 | 0.610 | measured |

Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.
