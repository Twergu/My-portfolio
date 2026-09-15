# SQLite vs pgvector benchmark

Generated: 2026-09-15T02:26:36.240219+00:00

Seed: 20260914; vectors: 1000; dimensions: 384; queries: 20; repeats: 3.

| Backend | Status | Query p50 (ms) | Query p95 (ms) | Recall@k | Indexing (ms) | HNSW build (ms) |
|---|---|---:|---:|---:|---:|---:|
| sqlite_exact | measured | 120.336 | 122.997 | 1.000 | 425.186 | — |
| pgvector_exact | measured | 2.539 | 2.591 | 1.000 | 334.560 | — |
| pgvector_hnsw | measured | 2.868 | 2.929 | 0.990 | 334.560 | 195.531 |

Missing measurements are not estimated. No speedup claim is made until both databases have been measured.

The exact reference is an independent float64 brute-force calculation. Warmup is excluded. Storage results do not measure document relevance or answer quality.

Run with a real PostgreSQL + pgvector database:

```sh
export RAG_BENCHMARK_DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/DATABASE"
python -m scripts.benchmark_stores --count 1000 --dimensions 384 --queries 20 --repeats 3
```

Only a randomly named `kb_bench_...` schema is created and removed; application tables are untouched.

For a larger comparison, repeat at multiple corpus sizes and at the actual Embedding model dimension. Exact supports up to 16000 dimensions; this implementation rejects HNSW above 2000 dimensions.
