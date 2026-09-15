# pgvector Exact vs HNSW — scale benchmark

Status: **completed**; run: 2026-09-15T02:27:27.625211+00:00

Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.

| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 2.506 | 2.654 | 1.000 | measured |
| 1000 | HNSW ef=100 | 2.787 | 3.085 | 1.000 | measured |
| 1000 | HNSW ef=400 | 3.205 | 3.256 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 3.770 | 3.820 | 1.000 | measured |
| 10000 | exact | 8.216 | 8.301 | 1.000 | measured |
| 10000 | HNSW ef=100 | 3.597 | 3.791 | 0.580 | measured |
| 10000 | HNSW ef=400 | 5.399 | 5.498 | 0.910 | measured |
| 10000 | HNSW ef=1000 | 7.401 | 9.426 | 1.000 | measured |
| 100000 | exact | 73.184 | 101.629 | 1.000 | measured |
| 100000 | HNSW ef=100 | 6.038 | 6.622 | 0.120 | measured |
| 100000 | HNSW ef=400 | 13.349 | 14.214 | 0.380 | measured |
| 100000 | HNSW ef=1000 | 28.157 | 36.299 | 0.630 | measured |

Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.
