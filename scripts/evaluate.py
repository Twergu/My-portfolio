"""Run the seed benchmark in isolated storage. API calls require --mode api."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import environment_settings
from backend.providers import ModelError
from backend.rag import answer, chunks_from_pages, embed
from backend.store import Store
from evals.judge import EVALUATION_PROTOCOL, judge_answer
from evals.metrics import aggregate, answer_metrics, retrieval_at_cutoffs, retrieval_metrics

DEFAULT_DATASET = ROOT / "evals" / "dataset.json"
HARD_DATASET = ROOT / "evals" / "hard_dataset.json"


def load_dataset(path=DEFAULT_DATASET):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported dataset schema")
    documents = {document["id"]: document for document in data["documents"]}
    if len(documents) != len(data["documents"]):
        raise ValueError("Duplicate document ID")
    ids = set()
    for query in data["queries"]:
        if query["id"] in ids or query["split"] not in ("dev", "test"):
            raise ValueError("Duplicate query ID or invalid split")
        ids.add(query["id"])
        if query["answerable"] != bool(query["relevance"]):
            raise ValueError("Answerability and page ground truth disagree")
        if not query["document_ids"] or any(doc_id not in documents for doc_id in query["document_ids"]):
            raise ValueError("Missing document scope")
        for row in query["relevance"]:
            document = documents.get(row["document_id"])
            if not document or row["page"] not in {p["page"] for p in document["pages"]}:
                raise ValueError("Ground truth refers to a missing physical page")
            if row["document_id"] not in query["document_ids"] or row["grade"] not in (1, 2, 3):
                raise ValueError("Invalid relevance scope or grade")
    return data


def provider_and_metrics(mode):
    from backend.providers import OpenAICompatibleProvider
    from backend.telemetry import Metrics

    return OpenAICompatibleProvider() if mode == "api" else None, Metrics


def build_index(store, dataset, settings, api_key, provider, metrics=None):
    _, Metrics = provider_and_metrics("local")
    metrics = metrics if metrics is not None else Metrics()
    started = time.perf_counter()
    chunk_count = 0
    for document in dataset["documents"]:
        body = json.dumps(document["pages"], ensure_ascii=False).encode("utf-8")
        store.register_document(
            {
                "id": document["id"],
                "name": document["name"],
                "sha256": hashlib.sha256(body).hexdigest(),
                "size": len(body),
                "status": "embedding",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        with metrics.measure("chunking"):
            chunks = chunks_from_pages(document["pages"], settings.chunk_size, settings.chunk_overlap)
            # Stable IDs make equal-score tie breaking reproducible across runs
            # and configurations producing identical physical chunks.
            for chunk in chunks:
                identity = json.dumps(
                    [document["id"], chunk["page"], chunk["ordinal"], chunk["text"]], ensure_ascii=False
                )
                chunk["id"] = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        with metrics.measure("index_embedding"):
            vectors = embed([chunk["text"] for chunk in chunks], settings, api_key, provider=provider, metrics=metrics)
        with metrics.measure("storage"):
            store.commit_chunks(document["id"], chunks, vectors, settings.profile)
            store.update(document["id"], pages=len(document["pages"]))
        chunk_count += len(chunks)
    return {
        "chunk_count": chunk_count,
        "elapsed_ms": (time.perf_counter() - started) * 1000,
        "metrics": metrics.as_dict(),
    }


def evaluate_dataset(
    dataset,
    settings,
    split="test",
    api_key="",
    provider=None,
    only_ids=None,
    judge_model="",
    concurrency=1,
    progress=None,
    resume=None,
    checkpoint=None,
):
    if not 1 <= concurrency <= 4:
        raise ValueError("Evaluation concurrency must be between 1 and 4")
    queries = [
        query
        for query in dataset["queries"]
        if (split == "all" or query["split"] == split) and (not only_ids or query["id"] in only_ids)
    ]
    if not queries:
        raise ValueError("No queries selected")
    if settings.mode == "api" and not api_key:
        raise ValueError("RAG_API_KEY is required for an explicit paid API evaluation")
    resume = resume or {}
    rows = list(resume.get("queries", []))
    done = {row["id"] for row in rows}
    if len(done) != len(rows) or not done.issubset({q["id"] for q in queries}):
        raise ValueError("Checkpoint contains duplicate or out-of-scope queries")
    indexing_attempts = list(resume.get("indexing_attempts", []))
    owns_provider = provider is None
    if owns_provider:
        provider, _ = provider_and_metrics(settings.mode)
    try:
        with tempfile.TemporaryDirectory(prefix="rag-eval-") as folder:
            store = Store(Path(folder))
            _, Metrics = provider_and_metrics("local")
            index_metrics = Metrics()
            indexing_error = None
            try:
                indexing = build_index(store, dataset, settings, api_key, provider, metrics=index_metrics)
            except ModelError as exc:
                indexing_error = exc.code
                indexing = {
                    "status": "failed",
                    "error_code": exc.code,
                    "chunk_count": sum(doc["chunk_count"] for doc in store.all_documents()),
                    "elapsed_ms": index_metrics.as_dict()["elapsed_ms"],
                    "metrics": index_metrics.as_dict(),
                }
            indexing_attempts.append(indexing)
            if checkpoint:
                checkpoint({"queries": rows, "indexing_attempts": indexing_attempts})

            def evaluate_query(query):
                started = time.perf_counter()
                question_metrics = Metrics()
                error_code = None
                try:
                    result = answer(
                        store,
                        query["question"],
                        settings,
                        api_key,
                        query["document_ids"],
                        preferred_language=query["language"],
                        provider=provider,
                        metrics=question_metrics,
                        include_candidate=True,
                    )
                except ModelError as exc:
                    error_code = exc.code
                    result = {
                        "status": "provider_error",
                        "mode": settings.mode,
                        "answer": "",
                        "sources": [],
                        "claims": [],
                        "metrics": question_metrics.as_dict(),
                    }
                elapsed_ms = (time.perf_counter() - started) * 1000
                sources = result.get("retrieved_sources", result.get("sources", []))
                retrieval = retrieval_metrics(sources, query["relevance"], settings.top_k)
                retrieval.update(
                    retrieval_at_cutoffs(sources, query["relevance"], [k for k in (1, 3, 5) if k <= settings.top_k])
                )
                quality = answer_metrics(result, query)
                judge_metrics, judgment, judge_error = Metrics(), None, None
                candidate_judgment = None
                if settings.mode == "api" and not error_code:
                    try:
                        judgment = judge_answer(
                            result, query, dataset, settings, api_key, provider, judge_model, judge_metrics
                        )
                        quality.update(
                            {name: judgment[name] for name in ("answer_correctness", "citation_groundedness")}
                        )
                        if (
                            result["status"] == "unsupported_answer"
                            and result.get("evaluation_candidate")
                            and judge_model
                        ):
                            candidate_judgment = judge_answer(
                                result["evaluation_candidate"],
                                query,
                                dataset,
                                settings,
                                api_key,
                                provider,
                                judge_model,
                                judge_metrics,
                            )
                            quality["withheld_candidate_correctness"] = candidate_judgment["answer_correctness"]
                            quality["grounding_rejected_correct_and_grounded"] = float(
                                candidate_judgment["answer_correctness"] == 1
                                and candidate_judgment["citation_groundedness"] == 1
                            )
                    except ModelError as exc:
                        judge_error = exc.code
                if error_code:
                    # A failed operation is unknown, not a measured empty ranking
                    # or a correct refusal. Error counts remain visible in status_counts.
                    retrieval = dict.fromkeys(retrieval)
                    quality = {key: None for key in quality if key != "applicability"} | {
                        "applicability": "N/A: provider error"
                    }
                return {
                    "id": query["id"],
                    "language": query["language"],
                    "category": query["category"],
                    "answerable": query["answerable"],
                    "status": result["status"],
                    "error_code": error_code,
                    "retrieval": retrieval,
                    "answer_quality": quality,
                    "elapsed_ms": elapsed_ms,
                    "metrics": result.get("metrics", {}),
                    "answer": result["answer"],
                    "claims": result.get("claims", []),
                    "support": result.get("support"),
                    "judgment": judgment,
                    "judge_error": judge_error,
                    "judge_metrics": judge_metrics.as_dict(),
                    "candidate_judgment": candidate_judgment,
                    "evaluation_trace": {
                        "sources": result.get("sources", []),
                        "candidate": result.get("evaluation_candidate"),
                    },
                    "retrieved_pages": [
                        {"document_id": source["document_id"], "page": source["page"], "score": source["score"]}
                        for source in sources
                    ],
                }

            if indexing_error is None:
                with ThreadPoolExecutor(max_workers=concurrency) as executor:
                    for row in executor.map(evaluate_query, [q for q in queries if q["id"] not in done]):
                        rows.append(row)
                        if checkpoint:
                            checkpoint({"queries": rows, "indexing_attempts": indexing_attempts})
                        if progress:
                            progress(len(rows), len(queries), row)
            totals = aggregate(rows)
            costs = [attempt["metrics"].get("cost_usd") for attempt in indexing_attempts]
            costs.append(totals["cost_usd"]["total"] if rows else 0.0)
            judge_costs = [row["judge_metrics"]["cost_usd"] for row in rows]
            judge_cost = sum(judge_costs) if all(c is not None for c in judge_costs) else None
            costs.append(judge_cost)
            return {
                "schema_version": 1,
                "status": "failed" if indexing_error or any(row["error_code"] for row in rows) else "completed",
                "requested_query_count": len(queries),
                "indexing_error": indexing_error,
                "dataset_id": dataset["dataset_id"],
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "dataset_sha256": hashlib.sha256(
                    json.dumps(dataset, ensure_ascii=False, sort_keys=True).encode()
                ).hexdigest(),
                "split": split,
                "mode": settings.mode,
                "configuration": settings.model_dump(exclude={"base_url"}),
                "embedding_profile": settings.profile,
                "evaluation_protocol": EVALUATION_PROTOCOL,
                "quality_evaluation": {
                    "judge_model": judge_model or None,
                    "independent_model": bool(
                        judge_model and judge_model not in (settings.chat_model, settings.effective_verifier_model)
                    ),
                    "status": "not_applicable"
                    if settings.mode == "local"
                    else "not_configured"
                    if not judge_model
                    else "failed"
                    if indexing_error or any(r["judge_error"] or r["error_code"] for r in rows)
                    else "completed",
                    "judge_cost_usd": judge_cost,
                    "judge_errors": sum(bool(r["judge_error"]) for r in rows),
                },
                "endpoint_configured": bool(settings.base_url) if settings.mode == "api" else False,
                "concurrency": concurrency,
                "measurement": f"One pass with {concurrency} query worker(s); no warmup. Application latency excludes evaluator/queue time; Judge cost is separate.",
                "limitations": dataset["limitations"],
                "indexing": indexing,
                "indexing_attempts": indexing_attempts,
                "summary": totals,
                "run_cost_usd": sum(costs) if all(cost is not None for cost in costs) else None,
                "by_language": {
                    lang: aggregate([row for row in rows if row["language"] == lang])
                    for lang in sorted({row["language"] for row in rows})
                },
                "by_category": {
                    category: aggregate([row for row in rows if row["category"] == category])
                    for category in sorted({row["category"] for row in rows})
                },
                "queries": rows,
            }
    finally:
        if owns_provider and provider is not None:
            provider.close()


def display(value):
    return "N/A" if value is None else f"{value:.4f}" if isinstance(value, float) else str(value)


def markdown(report):
    summary = report["summary"]
    lines = [
        f"# RAG evaluation — {report['dataset_id']}",
        "",
        f"Mode: **{report['mode']}**; split: **{report['split']}**; queries: {summary['query_count']}.",
        "",
        f"Run status: {report['status']}; requested questions: {report.get('requested_query_count', summary['query_count'])}; indexing error: {report.get('indexing_error') or 'none'}.",
        "",
        "Synthetic seed only. Test results are not evidence of production accuracy.",
        "",
        "| Retrieval metric (macro, answerable only) | Mean | n |",
        "|---|---:|---:|",
    ]
    for key in ("recall_at_1", "recall_at_3", "recall_at_5", "mrr_at_k", "ndcg_at_k", "precision_at_k"):
        metric = summary["retrieval"].get(key, {"mean": None, "count": 0})
        lines.append(f"| {key} | {display(metric['mean'])} | {metric['count']} |")
    lines += [
        "",
        "Page ranks are de-duplicated from the returned chunk budget; precision divides by k, including unfilled slots.",
        "",
        "| Answer metric | Mean | n |",
        "|---|---:|---:|",
    ]
    for key, metric in summary["answer_quality"].items():
        lines.append(f"| {key} | {display(metric['mean'])} | {metric['count']} |")
    lines += [
        "",
        "Local mode has no generated answer: answer-quality metrics are N/A. Lexical coverage / token F1 do not establish semantic correctness. Runtime claim_groundedness is a verifier diagnostic; answer_correctness and citation_groundedness come from the separately configured evaluation Judge, not human labels.",
        "",
        "| Latency (ms) | p50 | p95 | n |",
        "|---|---:|---:|---:|",
    ]
    for key, metric in summary["latency_ms"].items():
        lines.append(f"| {key} | {display(metric['p50'])} | {display(metric['p95'])} | {metric['count']} |")
    lines += [
        "",
        f"Indexing: {report['indexing']['chunk_count']} chunks, {report['indexing']['elapsed_ms']:.2f} ms.",
        f"Total run API cost (USD): {display(report['run_cost_usd'])}. Unknown usage or missing configured prices stay null/N/A.",
        "",
        f"Application mean USD/query: {display(summary['cost_usd'].get('average_per_query'))}; reported tokens: {summary.get('token_usage')}.",
        f"Independent evaluation: {report.get('quality_evaluation')}. Judge latency and cost are excluded from application query metrics.",
        report["measurement"],
        "",
        "## Per question",
        "",
        "| ID | Type | Status | Recall@k | Lexical fact coverage | Total ms |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in report["queries"]:
        lines.append(
            f"| {row['id']} | {row['category']} | {row['status']} | {display(row['retrieval']['recall_at_k'])} | {display(row['answer_quality']['expected_facts_coverage_lexical'])} | {row['elapsed_ms']:.2f} |"
        )
    lines += ["", "## Limits", ""] + ["- " + limit for limit in report["limitations"]]
    return "\n".join(lines) + "\n"


def write_report(report, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("local", "api"), default="local")
    parser.add_argument("--split", choices=("dev", "test", "all"), default="test")
    parser.add_argument("--dataset", type=Path, default=HARD_DATASET)
    parser.add_argument("--judge-model", default=os.getenv("RAG_EVAL_JUDGE_MODEL", ""))
    parser.add_argument("--verification-mode", choices=("off", "fast", "strict"))
    parser.add_argument("--retrieval-mode", choices=("dense", "hybrid"), default="dense")
    parser.add_argument("--reranker-mode", choices=("off", "llm"), default="off")
    parser.add_argument("--verification-strategy", choices=("all", "selective"), default="all")
    parser.add_argument("--verifier-prompt", choices=("baseline", "calibrated"), default="baseline")
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--overlap", type=int, default=120)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--concurrency", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    settings = environment_settings().model_copy(
        update={
            "mode": args.mode,
            "search_mode": "exact",
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.overlap,
            "top_k": args.top_k,
            "retrieval_mode": args.retrieval_mode,
            "reranker_mode": args.reranker_mode,
            "verification_strategy": args.verification_strategy,
            "verifier_prompt": args.verifier_prompt,
        }
    )
    settings = type(settings).model_validate(settings.model_dump())
    if args.verification_mode:
        settings.verification_mode = args.verification_mode
    if args.mode == "api" and not os.getenv("RAG_API_KEY"):
        parser.error("RAG_API_KEY is missing; no API request was made. Local mode needs no key.")
    from scripts.checkpoint import EvaluationCheckpoint, evaluation_identity

    dataset = load_dataset(args.dataset)
    output = args.output or ROOT / "evals" / "reports" / f"evaluation-{args.mode}-{args.split}"
    identity = evaluation_identity(dataset, settings, args.split, args.judge_model, args.concurrency)
    checkpoint = EvaluationCheckpoint(output.with_suffix(".checkpoint.json"), identity)
    resume = checkpoint.load()
    if output.with_suffix(".json").exists():
        prior = json.loads(output.with_suffix(".json").read_text(encoding="utf-8"))
        if (
            prior.get("checkpoint_identity") == identity
            and prior.get("status") == "completed"
            and prior.get("quality_evaluation", {}).get("status") in ("completed", "not_applicable")
        ):
            print("Compatible completed evaluation already exists; no API calls made.")
            return 0
    report = evaluate_dataset(
        dataset,
        settings,
        args.split,
        os.getenv("RAG_API_KEY", ""),
        judge_model=args.judge_model,
        concurrency=args.concurrency,
        progress=lambda done, total, row: print(f"{done}/{total}: {row['id']} {row['status']}", flush=True),
        resume=resume,
        checkpoint=checkpoint.save,
    )
    report["checkpoint_identity"] = identity
    write_report(report, output)
    print(f"Completed {report['summary']['query_count']} queries; report: {output.with_suffix('.md')}")
    return (
        0
        if report["status"] == "completed"
        and (args.mode == "local" or report["quality_evaluation"]["status"] == "completed")
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
