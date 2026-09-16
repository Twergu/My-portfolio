"""Paired dense / hybrid / hybrid+LLM ranking study using one common real index."""

import argparse
import hashlib
import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from backend.config import environment_settings
from backend.providers import ModelError, OpenAICompatibleProvider
from backend.rag import retrieve
from backend.store import Store
from backend.telemetry import Metrics
from evals.metrics import distribution, retrieval_at_cutoffs, retrieval_metrics
from scripts.evaluate import HARD_DATASET, build_index, load_dataset


def summarize(rows):
    keys = ["recall_at_1", "recall_at_3", "recall_at_5", "mrr_at_k", "ndcg_at_k"]

    def mean(xs):
        return sum(xs) / len(xs) if xs else None

    costs = [r["metrics"]["cost_usd"] for r in rows]
    return {
        "n": len(rows),
        "errors": sum(bool(r["error"]) for r in rows),
        "retrieval": {
            key: mean([r["retrieval"][key] for r in rows if r["retrieval"].get(key) is not None]) for key in keys
        },
        "latency_ms": distribution([r["metrics"]["elapsed_ms"] for r in rows]),
        "cost_usd": sum(costs) if all(c is not None for c in costs) else None,
        "mean_cost_usd": mean(costs) if all(c is not None for c in costs) else None,
        "tokens": sum(r["metrics"]["token_usage"]["total_tokens"] for r in rows),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("reports/v3/retrieval.json"))
    args = p.parse_args()
    settings = environment_settings().model_copy(
        update={
            "mode": "api",
            "chunk_size": 900,
            "chunk_overlap": 0,
            "top_k": 5,
            "candidate_k": 20,
            "search_mode": "exact",
        }
    )
    if not os.getenv("RAG_API_KEY"):
        p.error("RAG_API_KEY is missing")
    dataset = load_dataset(HARD_DATASET)
    identity = {
        "dataset_sha256": hashlib.sha256(json.dumps(dataset, sort_keys=True).encode()).hexdigest(),
        "settings": settings.model_dump(exclude={"base_url"}),
        "profile": settings.profile,
        "protocol": "paired-retrieval-v1",
    }
    rows, indexes = [], []
    if args.output.exists():
        previous = json.loads(args.output.read_text(encoding="utf-8"))
        if previous["identity"] != identity:
            raise ValueError("Resume identity mismatch")
        rows, indexes = previous["queries"], previous["indexing_attempts"]
    variants = {"dense": ("dense", "off"), "hybrid": ("hybrid", "off"), "hybrid_reranked": ("hybrid", "llm")}
    done = {(r["id"], r["variant"]) for r in rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    total = len(dataset["queries"]) * len(variants)

    def save():
        report = {
            "identity": identity,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed" if len(rows) == total and all(not r["error"] for r in rows) else "incomplete",
            "limitations": [
                "Synthetic benchmark; human review deferred.",
                "Existing test split is a regression benchmark, not a new unseen holdout.",
                "No generation or verification in this ranking study. All variants use real query embeddings; index shared, concurrency 2.",
            ],
            "indexing_attempts": indexes,
            "summary": {
                split: {
                    name: summarize([r for r in rows if r["split"] == split and r["variant"] == name])
                    for name in variants
                }
                for split in ("dev", "test")
            },
            "queries": rows,
        }
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if len(done) == total:
        return
    with OpenAICompatibleProvider() as provider, tempfile.TemporaryDirectory(prefix="kb-ranking-") as folder:
        store = Store(folder)
        indexes.append(build_index(store, dataset, settings, os.environ["RAG_API_KEY"], provider))
        save()

        def run(job):
            query, name = job
            config = settings.model_copy(
                update=dict(zip(("retrieval_mode", "reranker_mode"), variants[name], strict=True))
            )
            metrics, error = Metrics(), None
            try:
                sources = retrieve(
                    store,
                    query["question"],
                    config,
                    os.environ["RAG_API_KEY"],
                    query["document_ids"],
                    provider,
                    metrics,
                )
                values = retrieval_metrics(sources, query["relevance"], 5) | retrieval_at_cutoffs(
                    sources, query["relevance"]
                )
            except ModelError as exc:
                error, sources, values = exc.code, [], {}
            return {
                "id": query["id"],
                "split": query["split"],
                "variant": name,
                "category": query["category"],
                "language": query["language"],
                "error": error,
                "retrieval": values,
                "sources": sources,
                "metrics": metrics.as_dict(),
            }

        # Split then question then variant reduces order/time drift between arms.
        jobs = [
            (q, name)
            for split in ("dev", "test")
            for q in dataset["queries"]
            if q["split"] == split
            for name in variants
            if (q["id"], name) not in done
        ]
        with ThreadPoolExecutor(max_workers=2) as pool:
            for row in pool.map(run, jobs):
                rows.append(row)
                save()
                print(f"{len(rows)}/{total} {row['id']} {row['variant']} error={row['error']}", flush=True)
        store.close()


if __name__ == "__main__":
    main()
