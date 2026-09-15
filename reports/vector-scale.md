# pgvector Exact vs HNSW — scale benchmark

Status: **completed**; run: 2026-09-15T06:20:09.889643+00:00

Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.

| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 3.268 | 3.518 | 1.000 | measured |
| 1000 | HNSW ef=100 | 3.913 | 3.969 | 1.000 | measured |
| 1000 | HNSW ef=400 | 4.348 | 4.416 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 5.096 | 5.263 | 1.000 | measured |
| 10000 | exact | 11.071 | 11.592 | 1.000 | measured |
| 10000 | HNSW ef=100 | 4.755 | 4.943 | 0.550 | measured |
| 10000 | HNSW ef=400 | 6.901 | 7.112 | 0.940 | measured |
| 10000 | HNSW ef=1000 | 9.339 | 9.615 | 1.000 | measured |
| 100000 | exact | 102.249 | 144.143 | 1.000 | measured |
| 100000 | HNSW ef=100 | 8.203 | 8.912 | 0.140 | measured |
| 100000 | HNSW ef=400 | 18.210 | 25.858 | 0.390 | measured |
| 100000 | HNSW ef=1000 | 39.492 | 42.846 | 0.690 | measured |

Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.
