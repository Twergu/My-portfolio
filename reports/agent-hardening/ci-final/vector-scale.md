# pgvector Exact vs HNSW — scale benchmark

Status: **completed**; run: 2026-10-05T01:05:09.552242+00:00

Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.

| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 3.257 | 3.365 | 1.000 | measured |
| 1000 | HNSW ef=100 | 3.899 | 3.968 | 1.000 | measured |
| 1000 | HNSW ef=400 | 4.306 | 4.430 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 5.067 | 5.332 | 1.000 | measured |
| 10000 | exact | 10.304 | 10.639 | 1.000 | measured |
| 10000 | HNSW ef=100 | 4.649 | 7.372 | 0.600 | measured |
| 10000 | HNSW ef=400 | 7.038 | 10.672 | 0.960 | measured |
| 10000 | HNSW ef=1000 | 8.688 | 8.880 | 1.000 | measured |
| 100000 | exact | 101.508 | 132.877 | 1.000 | measured |
| 100000 | HNSW ef=100 | 7.534 | 8.198 | 0.130 | measured |
| 100000 | HNSW ef=400 | 17.209 | 24.827 | 0.350 | measured |
| 100000 | HNSW ef=1000 | 34.543 | 37.563 | 0.590 | measured |

Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.
