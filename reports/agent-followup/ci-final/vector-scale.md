# pgvector Exact vs HNSW — scale benchmark

Status: **completed**; run: 2026-10-05T12:33:38.664119+00:00

Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.

| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 2.781 | 2.887 | 1.000 | measured |
| 1000 | HNSW ef=100 | 3.161 | 3.300 | 1.000 | measured |
| 1000 | HNSW ef=400 | 3.624 | 5.179 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 4.257 | 4.432 | 1.000 | measured |
| 10000 | exact | 13.115 | 13.762 | 1.000 | measured |
| 10000 | HNSW ef=100 | 4.459 | 4.742 | 0.550 | measured |
| 10000 | HNSW ef=400 | 7.400 | 7.737 | 0.910 | measured |
| 10000 | HNSW ef=1000 | 10.834 | 11.297 | 1.000 | measured |
| 100000 | exact | 111.236 | 125.633 | 1.000 | measured |
| 100000 | HNSW ef=100 | 9.081 | 10.133 | 0.130 | measured |
| 100000 | HNSW ef=400 | 24.142 | 30.982 | 0.350 | measured |
| 100000 | HNSW ef=1000 | 52.500 | 53.898 | 0.670 | measured |

Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.
