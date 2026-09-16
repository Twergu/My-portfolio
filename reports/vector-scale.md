# pgvector Exact vs HNSW — scale benchmark

Status: **completed**; run: 2026-09-16T00:38:40.289783+00:00

Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.

| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 2.331 | 2.380 | 1.000 | measured |
| 1000 | HNSW ef=100 | 2.718 | 3.389 | 1.000 | measured |
| 1000 | HNSW ef=400 | 3.121 | 3.257 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 3.737 | 5.257 | 1.000 | measured |
| 10000 | exact | 8.328 | 9.768 | 1.000 | measured |
| 10000 | HNSW ef=100 | 3.408 | 3.568 | 0.600 | measured |
| 10000 | HNSW ef=400 | 5.116 | 5.268 | 0.910 | measured |
| 10000 | HNSW ef=1000 | 7.001 | 7.216 | 1.000 | measured |
| 100000 | exact | 91.499 | 105.971 | 1.000 | measured |
| 100000 | HNSW ef=100 | 7.254 | 8.119 | 0.150 | measured |
| 100000 | HNSW ef=400 | 17.810 | 18.870 | 0.400 | measured |
| 100000 | HNSW ef=1000 | 37.490 | 38.937 | 0.670 | measured |

Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.
