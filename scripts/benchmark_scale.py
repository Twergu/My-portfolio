"""Real pgvector exact/HNSW at 1k/10k/100k, with independent NumPy truth."""

import argparse
import hashlib
import json
import os
import platform
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from backend.config import environment_database_url
from backend.search_policy import ann_acceptance
from scripts.benchmark_stores import measure


def run_scale(count, dimensions, query_count, repeats, top_k, seed, url):
    import numpy as np
    import psycopg
    from psycopg import sql

    from backend.postgres_store import PostgresStore

    rng = np.random.default_rng(seed)
    vectors = rng.standard_normal((count, dimensions))
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    queries = rng.standard_normal((query_count, dimensions))
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)
    truth = [{f"chunk-{i:08d}" for i in np.argsort(vectors @ query)[-top_k:]} for query in queries]
    report = {
        "count": count,
        "dimensions": dimensions,
        "queries": query_count,
        "seed": seed,
        "vectors_sha256": hashlib.sha256(vectors.tobytes()).hexdigest(),
        "status": "running",
    }
    schema = "kb_scale_" + uuid.uuid4().hex
    pg = None
    with tempfile.TemporaryDirectory(prefix="pg-scale-") as folder:
        try:
            pg = PostgresStore(Path(folder), url, schema=schema, recover=False)
            started = time.perf_counter()
            pg.register_document(
                {
                    "id": "scale",
                    "name": "synthetic.pdf",
                    "sha256": "synthetic",
                    "size": 0,
                    "status": "embedding",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            # Stream rows in one transaction; never duplicate a 100k-vector Python
            # list. Timed ingestion uses the same production schema and constraints.
            with pg.connect() as db:
                with db.cursor().copy(
                    "COPY chunks(id,document_id,page,ordinal,text,vector,profile,dimensions) FROM STDIN"
                ) as copy:
                    for i, vector in enumerate(vectors):
                        copy.write_row(
                            (
                                f"chunk-{i:08d}",
                                "scale",
                                i // 20 + 1,
                                i,
                                "Synthetic vector",
                                json.dumps(vector.tolist()),
                                "scale",
                                dimensions,
                            )
                        )
                db.execute(
                    "UPDATE documents SET status='ready',profile='scale',dimensions=%s,chunk_count=%s WHERE id='scale'",
                    (dimensions, count),
                )
                db.execute("ANALYZE chunks")
                report["postgres_version"] = db.execute("SHOW server_version").fetchone()["server_version"]
                report["pgvector_version"] = db.execute(
                    "SELECT extversion FROM pg_extension WHERE extname='vector'"
                ).fetchone()["extversion"]
                report["chunks_bytes_before_hnsw"] = db.execute(
                    "SELECT pg_total_relation_size('chunks') AS n"
                ).fetchone()["n"]
            report["ingestion_ms"] = (time.perf_counter() - started) * 1000
            query_list = queries.tolist()
            report["exact"] = measure(pg, query_list, truth, "scale", top_k, repeats, "exact")
            started = time.perf_counter()
            pg.prepare_index("scale", dimensions)
            report["hnsw_build_ms"] = (time.perf_counter() - started) * 1000
            report["hnsw_sweep"] = {
                str(ef): measure(pg, query_list, truth, "scale", top_k, repeats, "hnsw", ef_search=ef)
                for ef in (100, 400, 1000)
            }
            report["hnsw"] = report["hnsw_sweep"]["100"]
            report["ann_acceptance"] = {
                ef: ann_acceptance(report["exact"], result) for ef, result in report["hnsw_sweep"].items()
            }
            with pg.connect() as db:
                report["hnsw_index_bytes"] = db.execute(
                    "SELECT pg_relation_size(%s::regclass) AS n", (pg.index_name("scale", dimensions),)
                ).fetchone()["n"]
            report["hnsw_index_used"] = all(row.get("hnsw_index_used") for row in report["hnsw_sweep"].values())
            report["status"] = (
                "measured" if report["exact"]["status"] == "measured" and report["hnsw_index_used"] else "failed"
            )
        except Exception as exc:
            report.update(status="failed", error_type=type(exc).__name__)
        finally:
            if pg:
                pg.close()
            with psycopg.connect(url, autocommit=True, connect_timeout=10) as db:
                db.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema)))
    return report


def write(report, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# pgvector Exact vs HNSW — scale benchmark",
        "",
        f"Status: **{report['status']}**; run: {report['generated_at']}",
        "",
        "Synthetic normalized Gaussian vectors; warm single-client queries, independent float64 NumPy truth. HNSW ef_search=100/400/1000, default m=16/ef_construction=64. COPY ingestion is timed separately from index build. Plans use the production SQL and server-cursor context. Explicit HNSW mode disables sequential/bitmap scans and sorting to prevent an exact fallback; exact mode disables index/bitmap scans.",
        "",
        "| Chunks | Search | p50 ms | p95 ms | Recall@K | Status |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for row in report["results"]:
        measurements = {"exact": row.get("exact", {})}
        measurements.update({f"HNSW ef={ef}": result for ef, result in row.get("hnsw_sweep", {}).items()})
        for mode, result in measurements.items():

            def fmt(n):
                return "—" if n is None else f"{n:.3f}"

            lines.append(
                f"| {row['count']} | {mode} | {fmt(result.get('query_latency_ms', {}).get('p50'))} | {fmt(result.get('query_latency_ms', {}).get('p95'))} | {fmt(result.get('recall_at_k_against_independent_exact'))} | {row['status']} |"
            )
    lines += [
        "",
        "Choose Exact if its measured p95 meets the application SLO. Choose HNSW only when its measured recall also meets the quality target. This synthetic corpus does not establish a universal switching threshold. Index sizes, build time, query plan, machine and software versions are in JSON. Missing service results are not estimated.",
    ]
    output.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=[1000, 10000, 100000])
    parser.add_argument("--dimensions", type=int, default=384)
    parser.add_argument("--queries", type=int, default=20)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260914)
    parser.add_argument("--database-url-env", default="RAG_BENCHMARK_DATABASE_URL")
    parser.add_argument("--output", type=Path, default=Path("reports/vector-scale"))
    args = parser.parse_args()
    if (
        not 1 <= args.dimensions <= 2000
        or min(args.sizes) < args.top_k
        or min(args.queries, args.repeats, args.top_k) < 1
    ):
        parser.error("Invalid benchmark sizes or dimensions.")
    url = (
        environment_database_url()
        if args.database_url_env == "RAG_DATABASE_URL"
        else os.getenv(args.database_url_env, "")
    )
    report = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "running" if url else "blocked",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
        },
        "parameters": vars(args) | {"output": str(args.output)},
        "results": [],
    }
    for size in args.sizes:
        row = (
            run_scale(size, args.dimensions, args.queries, args.repeats, args.top_k, args.seed, url)
            if url
            else {"count": size, "status": "blocked", "reason": "PostgreSQL URL is not configured."}
        )
        report["results"].append(row)
        write(report, args.output)
        print(f"{size}: {row['status']}", flush=True)
    report["status"] = (
        "completed" if all(row["status"] == "measured" for row in report["results"]) else "failed" if url else "blocked"
    )
    write(report, args.output)
    return 0 if report["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
