# pgvector Exact vs HNSW — scale benchmark

Status: **completed**; run: 2026-09-16T00:26:51.735067+00:00

Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.

| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 2.366 | 2.401 | 1.000 | measured |
| 1000 | HNSW ef=100 | 2.776 | 3.833 | 1.000 | measured |
| 1000 | HNSW ef=400 | 3.191 | 3.254 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 3.740 | 3.829 | 1.000 | measured |
| 10000 | exact | 8.425 | 9.372 | 1.000 | measured |
| 10000 | HNSW ef=100 | 3.479 | 3.705 | 0.560 | measured |
| 10000 | HNSW ef=400 | 5.117 | 5.459 | 0.950 | measured |
| 10000 | HNSW ef=1000 | 7.134 | 10.760 | 0.990 | measured |
| 100000 | exact | 92.388 | 100.690 | 1.000 | measured |
| 100000 | HNSW ef=100 | 7.218 | 7.759 | 0.170 | measured |
| 100000 | HNSW ef=400 | 18.337 | 19.528 | 0.350 | measured |
| 100000 | HNSW ef=1000 | 39.664 | 41.716 | 0.570 | measured |

Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.
