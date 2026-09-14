"""Reproducible SQLite JSON vectors vs pgvector exact/HNSW benchmark.

No Embedding or LLM requests are made. The same seeded, normalized vectors and
queries are used for every backend. Set RAG_BENCHMARK_DATABASE_URL to include a
real PostgreSQL run; only a uniquely named temporary schema is created/deleted.
"""
import argparse
import hashlib
import heapq
import json
import math
import os
import platform
import random
import statistics
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from backend.config import ROOT  # Loads the project's optional .env once.
from backend.store import Store


def percentile(values, fraction):
    ordered = sorted(values)
    point = (len(ordered) - 1) * fraction
    lower = math.floor(point)
    upper = math.ceil(point)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (point - lower)


def summarize(values):
    return {'count': len(values), 'mean': statistics.mean(values),
            'p50': percentile(values, .5), 'p95': percentile(values, .95)}


def generate(seed, count, dimensions, query_count):
    rng = random.Random(seed)
    def vector():
        raw = [rng.gauss(0, 1) for _ in range(dimensions)]
        norm = math.hypot(*raw)
        return [value / norm for value in raw]
    vectors = [vector() for _ in range(count)]
    queries = [vector() for _ in range(query_count)]
    return vectors, queries


def prepare(store, vectors, profile):
    store.register_document({'id': 'benchmark-document', 'name': 'synthetic-benchmark.pdf',
                             'sha256': 'synthetic-only', 'size': 0, 'status': 'queued',
                             'created_at': datetime.now(timezone.utc).isoformat()})
    chunks = [{'id': f'chunk-{i:08d}', 'page': 1, 'ordinal': i, 'text': f'Seeded synthetic vector {i}.'}
              for i in range(len(vectors))]
    started = time.perf_counter()
    store.accept_dimensions(profile, len(vectors[0]))
    store.update('benchmark-document', pages=1)
    store.commit_chunks('benchmark-document', chunks, vectors, profile)
    return (time.perf_counter() - started) * 1000


def measure(store, queries, truth, profile, top_k, repeats, mode):
    for query in queries:  # One complete warmup pass, excluded from measurements.
        store.search(query, profile, top_k=top_k, mode=mode)
    timings, recalls = [], []
    for _ in range(repeats):
        for query, expected in zip(queries, truth, strict=True):
            started = time.perf_counter()
            rows = store.search(query, profile, top_k=top_k, mode=mode)
            timings.append((time.perf_counter() - started) * 1000)
            recalls.append(len({row['id'] for row in rows}.intersection(expected)) / len(expected))
    return {'status': 'measured', 'query_latency_ms': summarize(timings),
            'recall_at_k_against_independent_exact': statistics.mean(recalls),
            'minimum_query_recall': min(recalls), 'warmup_query_count': len(queries)}


def run_benchmark(*, count=1000, dimensions=384, query_count=20, repeats=3, top_k=5,
                  seed=20260914, database_url=None, work_dir=None):
    if count < top_k or min(count, dimensions, query_count, repeats, top_k) < 1 or dimensions > 16000:
        raise ValueError('Invalid benchmark dimensions, counts or k.')
    vectors, queries = generate(seed, count, dimensions, query_count)
    digest = hashlib.sha256(json.dumps([vectors, queries], separators=(',', ':')).encode()).hexdigest()
    # Independent float64 brute-force reference, not the SQLite search method.
    truth = [{f'chunk-{i:08d}' for _, i in heapq.nlargest(top_k,
              ((sum(a * b for a, b in zip(query, vector)), i) for i, vector in enumerate(vectors)))}
             for query in queries]
    report = {'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(),
              'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                              'cpu_count': os.cpu_count()},
              'dataset': {'kind': 'synthetic-normalized-gaussian', 'seed': seed, 'vectors': count,
                          'dimensions': dimensions, 'queries': query_count, 'sha256': digest},
              'method': {'top_k': top_k, 'repeats': repeats, 'concurrency': 1,
                         'distance': 'cosine', 'hnsw_ef_search': 100,
                         'timing_scope': 'store.search including DB connection acquisition and row decoding; excludes model calls',
                         'recall_reference': 'independent Python float64 brute-force dot product on normalized vectors',
                         'cache_state': 'warm, one full query pass excluded',
                         'limitations': ['Synthetic vectors measure storage/search, not semantic RAG answer quality.',
                                        'Single machine/client and one data scale; do not infer production speedups.',
                                        'PostgreSQL stores float32; exact tie/rounding differences can affect recall.',
                                        'SQLite opens per-call connections; PostgreSQL reuses a connection pool.']},
              'backends': {}}
    profile = 'benchmark-' + str(seed)
    with tempfile.TemporaryDirectory(prefix='store-benchmark-', dir=work_dir) as tmp:
        sqlite = Store(Path(tmp) / 'sqlite')
        indexing = prepare(sqlite, vectors, profile)
        report['backends']['sqlite_exact'] = measure(sqlite, queries, truth, profile, top_k, repeats, 'exact') | {
            'indexing_ms': indexing, 'hnsw_index_build_ms': None,
            'database_file_bytes': sqlite.path.stat().st_size}
        sqlite.close()
        if not database_url:
            report['backends']['pgvector_exact'] = {'status': 'blocked', 'reason': 'RAG_BENCHMARK_DATABASE_URL is not configured; no PostgreSQL measurement was made.'}
            report['backends']['pgvector_hnsw'] = {'status': 'blocked', 'reason': 'RAG_BENCHMARK_DATABASE_URL is not configured; no PostgreSQL measurement was made.'}
        else:
            from backend.postgres_store import PostgresStore
            import psycopg
            from psycopg import sql
            schema = 'kb_bench_' + uuid.uuid4().hex
            pg = None
            try:
                pg = PostgresStore(Path(tmp) / 'pgvector', database_url, schema=schema, recover=False)
                indexing = prepare(pg, vectors, profile)
                with pg.connect() as db:
                    db.execute('ANALYZE chunks')
                    version = db.execute("SELECT extversion FROM pg_extension WHERE extname='vector'").fetchone()['extversion']
                    postgres_version = db.execute('SHOW server_version').fetchone()['server_version']
                    storage_bytes = db.execute("SELECT pg_total_relation_size('chunks') AS bytes").fetchone()['bytes']
                report['environment'].update({'postgresql': postgres_version, 'pgvector': version})
                report['backends']['pgvector_exact'] = measure(pg, queries, truth, profile, top_k, repeats, 'exact') | {
                    'indexing_ms': indexing, 'chunks_relation_bytes': storage_bytes, 'hnsw_index_build_ms': None}
                if dimensions > 2000:
                    report['backends']['pgvector_hnsw'] = {'status': 'unsupported', 'reason': 'HNSW vector requires <=2000 dimensions; this benchmark does not silently truncate or quantize.'}
                else:
                    started = time.perf_counter()
                    pg.prepare_index(profile, dimensions)
                    build_ms = (time.perf_counter() - started) * 1000
                    report['backends']['pgvector_hnsw'] = measure(pg, queries, truth, profile, top_k, repeats, 'hnsw') | {
                        'indexing_ms': indexing, 'hnsw_index_build_ms': build_ms}
            except Exception as exc:
                # Avoid persisting a DSN/password or driver exception containing secrets.
                for name in ('pgvector_exact', 'pgvector_hnsw'):
                    report['backends'].setdefault(name, {'status': 'failed', 'error_type': type(exc).__name__,
                                                        'reason': 'PostgreSQL benchmark failed; verify the connection, extension and schema privileges.'})
            finally:
                if pg is not None:
                    pg.close()
                try:
                    with psycopg.connect(database_url, autocommit=True, connect_timeout=10) as cleanup:
                        cleanup.execute(sql.SQL('DROP SCHEMA IF EXISTS {} CASCADE').format(sql.Identifier(schema)))
                except Exception as exc:
                    report['cleanup'] = {'status': 'failed', 'error_type': type(exc).__name__, 'schema': schema}
    report['comparison_complete'] = all(row['status'] == 'measured' for row in report['backends'].values()) and report.get('cleanup', {}).get('status') != 'failed'
    return report


def markdown(report):
    dataset = report['dataset']
    lines = ['# SQLite vs pgvector benchmark', '', f"Generated: {report['created_at']}", '',
             f"Seed: {dataset['seed']}; vectors: {dataset['vectors']}; dimensions: {dataset['dimensions']}; queries: {dataset['queries']}; repeats: {report['method']['repeats']}.", '',
             '| Backend | Status | Query p50 (ms) | Query p95 (ms) | Recall@k | Indexing (ms) | HNSW build (ms) |',
             '|---|---|---:|---:|---:|---:|---:|']
    for name, row in report['backends'].items():
        def number(value):
            return f'{value:.3f}' if value is not None else '—'
        timing = row.get('query_latency_ms', {})
        lines.append(f"| {name} | {row['status']} | {number(timing.get('p50'))} | {number(timing.get('p95'))} | {number(row.get('recall_at_k_against_independent_exact'))} | {number(row.get('indexing_ms'))} | {number(row.get('hnsw_index_build_ms'))} |")
    lines += ['', 'Missing measurements are not estimated. No speedup claim is made until both databases have been measured.', '',
              'The exact reference is an independent float64 brute-force calculation. Warmup is excluded. Storage results do not measure document relevance or answer quality.', '',
              'Run with a real PostgreSQL + pgvector database:', '', '```sh',
              'export RAG_BENCHMARK_DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/DATABASE"',
              'python -m scripts.benchmark_stores --count 1000 --dimensions 384 --queries 20 --repeats 3', '```', '',
              'Only a randomly named `kb_bench_...` schema is created and removed; application tables are untouched.', '',
              'For a larger comparison, repeat at multiple corpus sizes and at the actual Embedding model dimension. Exact supports up to 16000 dimensions; this implementation rejects HNSW above 2000 dimensions.']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, default=1000)
    parser.add_argument('--dimensions', type=int, default=384)
    parser.add_argument('--queries', type=int, default=20)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--top-k', type=int, default=5)
    parser.add_argument('--seed', type=int, default=20260914)
    parser.add_argument('--database-url-env', default='RAG_BENCHMARK_DATABASE_URL')
    parser.add_argument('--output', type=Path, default=Path('reports/store-benchmark.json'))
    parser.add_argument('--require-postgres', action='store_true', help='Exit nonzero unless both pgvector measurements complete.')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = run_benchmark(count=args.count, dimensions=args.dimensions, query_count=args.queries,
                           repeats=args.repeats, top_k=args.top_k, seed=args.seed,
                           database_url=os.getenv(args.database_url_env), work_dir=args.output.parent)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    args.output.with_suffix('.md').write_text(markdown(report), encoding='utf-8')
    print(json.dumps({'report': str(args.output), 'comparison_complete': report['comparison_complete'],
                      'backends': {name: row['status'] for name, row in report['backends'].items()}}, ensure_ascii=False))
    return 2 if args.require_postgres and not report['comparison_complete'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
