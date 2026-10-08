"""Generate v3 tables and diagnostics from measured reports, not constants."""

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from backend.verification import needs_semantic_verification
from scripts.evaluate import HARD_DATASET, load_dataset

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    path = ROOT / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def selective_audit(report):
    queries = {q["id"]: q for q in load_dataset(HARD_DATASET)["queries"]}
    total, skipped, candidates, calls_avoided = 0, 0, 0, 0
    for row in report["queries"]:
        candidate = row.get("evaluation_trace", {}).get("candidate")
        if not candidate:
            continue
        candidates += 1
        source_map = {s["number"]: s for s in candidate["sources"]}
        selected = 0
        for index, claim in enumerate(candidate["claims"], 1):
            total += 1
            payload = {
                "claim_index": index,
                "text": claim["text"],
                "cited_passages": [
                    {"source_id": e["source_id"], "quote": e["quote"], "text": source_map[e["source_id"]]["text"]}
                    for e in claim["evidence"]
                ],
            }
            check = needs_semantic_verification(queries[row["id"]]["question"], payload)
            selected += check
            skipped += not check
        calls_avoided += selected == 0
    return {
        "protocol": "Offline deterministic policy replay on fixed generated candidates; no new LLM calls",
        "candidate_answers": candidates,
        "claims": total,
        "skip_eligible_claims": skipped,
        "fully_avoidable_verifier_calls": calls_avoided,
        "observed_potential_call_reduction": calls_avoided / candidates if candidates else None,
        "measured_selective_api_latency": None,
        "limitation": "Skipping some claims in a batch does not remove the verifier call. Latency/cost savings are not assumed.",
    }


def role_usage(report):
    values = {}
    for row in report["queries"]:
        for call in row["metrics"]["requests"]:
            role = call["role"]
            entry = values.setdefault(role, {"attempts": 0, "tokens": 0, "http_ms": 0})
            entry["attempts"] += 1
            entry["tokens"] += call.get("token_usage", {}).get("total_tokens", 0)
            entry["http_ms"] += call["elapsed_ms"]
    return values


def quality_row(report):
    summary = report["summary"]
    return {
        "status": report["status"],
        "judge_status": report["quality_evaluation"]["status"],
        "n": summary["query_count"],
        "retrieval": {
            k: summary["retrieval"][k]["mean"]
            for k in ("recall_at_1", "recall_at_3", "recall_at_5", "mrr_at_k", "ndcg_at_k")
        },
        "quality": {
            k: summary["answer_quality"][k]
            for k in (
                "answer_correctness",
                "citation_groundedness",
                "refusal_accuracy",
                "false_refusal",
                "quote_match_failure",
                "unsupported_answer",
            )
        },
        "latency_ms": summary["latency_ms"]["question_total"],
        "phase_latency_ms": summary["latency_ms"],
        "mean_cost_usd": summary["cost_usd"]["average_per_query"],
        "token_usage": summary["token_usage"],
        "role_usage": role_usage(report),
        "validation_failures": dict(
            Counter(
                event["stage"] for row in report["queries"] for event in row["metrics"].get("validation_failures", [])
            )
        ),
        "run_cost_usd": report["run_cost_usd"],
    }


def build():
    retrieval = load("reports/v3/retrieval.json")
    quality = {}
    for mode in ("strict", "fast"):
        report = load(f"reports/v3/quality-{mode}-test.json")
        if report:
            quality[mode] = quality_row(report)
    strict = load("reports/v3/quality-strict-test.json")
    calibration = {
        name: load("reports/v3/" + name + ".json")
        for name in ("calibration-baseline-dev-live", "calibration-calibrated-dev", "calibration-calibrated-test")
    }
    entries = []
    if retrieval:
        costs = [i["metrics"]["cost_usd"] for i in retrieval["indexing_attempts"]] + [
            r["metrics"]["cost_usd"] for r in retrieval["queries"]
        ]
        entries.append(
            {"experiment": "paired_retrieval", "cost_usd": sum(costs) if all(c is not None for c in costs) else None}
        )
    entries += [{"experiment": name, "cost_usd": r["cost_usd"]} for name, r in calibration.items() if r]
    entries += [{"experiment": "quality_" + name, "cost_usd": r["run_cost_usd"]} for name, r in quality.items()]
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "retrieval": retrieval["summary"] if retrieval else None,
        "retrieval_errors": sum(bool(r["error"]) for r in retrieval["queries"]) if retrieval else None,
        "calibration": {name: r["summary"] for name, r in calibration.items() if r},
        "quality": quality,
        "selective_audit": selective_audit(strict) if strict else None,
        "cost_ledger": entries,
        "known_recorded_cost_usd": sum(r["cost_usd"] for r in entries if r["cost_usd"] is not None),
        "complete_total_cost_available": False,
        "cost_caveat": "The interrupted earlier quality run has unknown usage/cost; this subtotal is not the total invoice. Checkpoints and prior-release reports are not counted twice.",
        "limitations": [
            "Synthetic regression set, not human-reviewed business acceptance.",
            "Existing test split has been evaluated previously; it is not newly unseen.",
            "Reranking/generation are stochastic; differences are single-run observations.",
            "Independent LLM Judge can make errors; citation scores are not a formal guarantee.",
        ],
    }
    return result


def fmt(value, decimals=3):
    return "N/A" if value is None else f"{value:.{decimals}f}"


def render(result):
    lines = [
        "## v3 真实检索与回答质量",
        "",
        "数据来自保存的 JSON；54 道 test 问题（42 可回答、12 无答案），Luna / text-embedding-3-small，独立评估 Judge 为 gpt-4.1。",
        "",
        "| 检索方案 | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG | 检索 P50/P95 秒 | 错误 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if result["retrieval"]:
        for name, row in result["retrieval"]["test"].items():
            r = row["retrieval"]
            lines.append(
                f"| {name} | {fmt(r['recall_at_1'])} | {fmt(r['recall_at_3'])} | {fmt(r['recall_at_5'])} | {fmt(r['mrr_at_k'])} | {fmt(r['ndcg_at_k'])} | {fmt(row['latency_ms']['p50'] / 1000)}/{fmt(row['latency_ms']['p95'] / 1000)} | {row['errors']} |"
            )
    lines += [
        "",
        "三路检索报告的 dev 有 1 次格式错误，原始记录保留；后续代码加入一次有上限的格式修复。test 三组均无错误。",
        "",
        "| 完整 RAG | 正确率 / n | 引用有据 / n | 拒答准确率 | 误拒答率 | P50/P95 秒 | USD/query |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in result["quality"].items():
        q, t = row["quality"], row["latency_ms"]
        lines.append(
            f"| {name} | {fmt(q['answer_correctness']['mean'])} / {q['answer_correctness']['count']} | {fmt(q['citation_groundedness']['mean'])} / {q['citation_groundedness']['count']} | {fmt(q['refusal_accuracy']['mean'])} | {fmt(q['false_refusal']['mean'])} | {fmt(t['p50'] / 1000)}/{fmt(t['p95'] / 1000)} | {fmt(row['mean_cost_usd'], 6)} |"
        )
    lines += [
        "",
        "完整 RAG 和纯检索实验是不同运行，排序可能不同。费用为配置单价估算；USD/query 排除索引和离线 Judge。fast 没有语义 Verifier，自动 Judge 的高分不能替代运行时保障。",
        "",
    ]
    if result["selective_audit"]:
        a = result["selective_audit"]
        lines += [
            f"Selectivity 回放：{a['claims']} 条生成断言中 {a['skip_eligible_claims']} 条可跳过，完整可省去 {a['fully_avoidable_verifier_calls']} 次 Verifier 请求。这是对固定候选的离线策略检查，不是一次新的 API 延迟实验。",
            "",
        ]
    lines += [
        f"本轮可追溯实验费用小计 USD {fmt(result['known_recorded_cost_usd'], 6)}。此前中断运行的用量未知，不能把小计当成全部账单。",
        "",
        "数据集未经人工审核；这些结果只代表当前合成回归集。完整逐题原文、tokens、阶段耗时、失败及单价见 [v3 JSON](reports/v3/summary.json)。",
    ]
    return "\n".join(lines) + "\n"


def main():
    result = build()
    folder = ROOT / "reports" / "v3"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    text = render(result)
    (folder / "summary.md").write_text(text.replace("(reports/v3/summary.json)", "(summary.json)"), encoding="utf-8")
    readme = ROOT / "README.md"
    original = readme.read_text(encoding="utf-8")
    start, end = "<!-- V3_RESULTS_START -->", "<!-- V3_RESULTS_END -->"
    original = original.split(start)[0] + start + "\n" + text + end + original.split(end, 1)[1]
    readme.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    main()
