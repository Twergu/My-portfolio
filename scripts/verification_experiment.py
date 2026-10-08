"""Explicit paid off/fast/strict comparison with an independent reference judge."""

import argparse
import json
import os
from pathlib import Path

from backend.config import environment_settings
from scripts.chunk_experiment import reusable_report
from scripts.evaluate import HARD_DATASET, evaluate_dataset, load_dataset, provider_and_metrics, write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-api", action="store_true", required=True, help="Explicitly enable paid evaluation calls."
    )
    parser.add_argument("--dataset", type=Path, default=HARD_DATASET)
    parser.add_argument("--split", choices=("dev", "test"), default="test")
    parser.add_argument("--judge-model", default=os.getenv("RAG_EVAL_JUDGE_MODEL", ""))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/verification"))
    parser.add_argument("--concurrency", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--overlap", type=int, default=120)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    key = os.getenv("RAG_API_KEY", "")
    if not key or not args.judge_model:
        parser.error("API key and an explicit evaluation judge model are required.")
    settings = environment_settings().model_copy(
        update={"mode": "api", "search_mode": "exact", "chunk_size": args.chunk_size, "chunk_overlap": args.overlap}
    )
    settings = type(settings).model_validate(settings.model_dump())
    dataset = load_dataset(args.dataset)
    provider, _ = provider_and_metrics("api")
    reports = []
    try:
        for mode in ("off", "fast", "strict"):
            candidate = settings.model_copy(update={"verification_mode": mode})
            output = args.output_dir / mode
            report = (
                reusable_report(
                    output.with_suffix(".json"), dataset, candidate, args.split, args.judge_model, args.concurrency
                )
                if args.resume
                else None
            )
            if report is None:
                report = evaluate_dataset(
                    dataset,
                    candidate,
                    args.split,
                    key,
                    provider,
                    judge_model=args.judge_model,
                    concurrency=args.concurrency,
                    progress=lambda done, total, row, mode=mode: print(
                        f"{mode} {done}/{total}: {row['status']}", flush=True
                    ),
                )
            write_report(report, args.output_dir / mode)
            reports.append(
                {
                    "mode": mode,
                    "summary": report["summary"],
                    "quality_evaluation": report["quality_evaluation"],
                    "configuration": report["configuration"],
                    "concurrency": report["concurrency"],
                    "generated_at": report["generated_at"],
                    "run_cost_usd": report["run_cost_usd"],
                }
            )
            if report["status"] != "completed" or report["quality_evaluation"]["status"] != "completed":
                raise RuntimeError("Incomplete evaluation saved; comparison stopped.")
    finally:
        provider.close()
    (args.output_dir / "comparison.json").write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Verification mode comparison",
        "",
        f"Dataset: {dataset['dataset_id']}; split: {args.split}; chunk size/overlap: {args.chunk_size}/{args.overlap}; query workers: {args.concurrency}.",
        "",
        "Generator and verifier: "
        + settings.chat_model
        + " / "
        + settings.effective_verifier_model
        + "; independent Judge: "
        + args.judge_model
        + ".",
        "",
        "| Mode | Correctness | Citation groundedness | Refusal accuracy | Quote mismatch | Unsupported | False refusal | Query p50 ms | Query p95 ms | Mean query USD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in reports:
        quality = row["summary"]["answer_quality"]
        latency = row["summary"]["latency_ms"]["question_total"]
        values = [
            quality.get(key, {}).get("mean")
            for key in (
                "answer_correctness",
                "citation_groundedness",
                "refusal_accuracy",
                "quote_match_failure",
                "unsupported_answer",
                "false_refusal",
            )
        ]
        values += [latency["p50"], latency["p95"], row["summary"]["cost_usd"]["average_per_query"]]
        lines.append("| " + row["mode"] + " | " + " | ".join("N/A" if v is None else f"{v:.8f}" for v in values) + " |")
    lines += [
        "",
        "Citation groundedness is an independent evaluation of delivered answers; it is not the runtime verifier pass rate. Off/fast remain semantically unverified in the application. Correctness uses answerable questions; refusal accuracy uses all questions. See each mode JSON for denominators and rejected-candidate diagnostics.",
        "",
        "Query latency/cost excludes the extra evaluation Judge and indexing. One generation per question/mode; generation randomness remains a confounder, so this is a pipeline comparison, not a paired replay of identical candidate answers. Test scores are reported without tuning prompts on test failures.",
    ]
    (args.output_dir / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
