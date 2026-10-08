"""Generate the README's Agent table from complete saved API/CI reports."""

import json

from backend.config import ROOT


def main():
    folder = ROOT / "reports/agent-hardening"
    names = ("evaluation-baseline-live", "evaluation-guarded-handoff-live", "evaluation-final-quoted-live")
    reports = [json.loads((folder / f"{name}.json").read_text(encoding="utf-8")) for name in names]
    if not all(r["summary"]["complete"] for r in reports):
        raise SystemExit("Only complete evaluation runs may populate the README table")
    if len({r["dataset_sha256"] for r in reports}) != 1:
        raise SystemExit("The comparison requires an identical dataset")
    ci = json.loads((folder / "ci-final/provenance.json").read_text(encoding="utf-8"))
    start, end = "<!-- AGENT_RESULTS_START -->", "<!-- AGENT_RESULTS_END -->"
    lines = [
        start,
        "## Agent 真实评估与运行边界",
        "",
        "24 个独立中日英虚构任务；真实 Embedding、Planner、Generator、Strict/all Verifier 和独立 Judge。Calculator 为确定性计算，工作日日历明确为 Mock。数据未经人工审核，以下是回归实测，不是生产准确率保证。",
        "",
        "| 指标 | 基线 | 交接优化 | 最终证据/状态加固 |",
        "| --- | ---: | ---: | ---: |",
    ]
    summaries = [r["summary"] for r in reports]
    for label, key in (
        ("Task Success", "task_success"),
        ("Planning Success", "planning_success"),
        ("Tool Selection Accuracy", "tool_selection_accuracy"),
        ("Clarification Accuracy", "clarification_accuracy"),
        ("Answer Correctness", "answer_correctness"),
        ("Grounded Answer Rate", "grounded_answer_rate"),
    ):
        lines.append(f"| {label} | " + " | ".join(f"{s[key]:.1%}" for s in summaries) + " |")
    lines.append(
        "| P50 / P95 秒 | "
        + " | ".join(f"{s['latency_ms']['p50'] / 1000:.2f} / {s['latency_ms']['p95'] / 1000:.2f}" for s in summaries)
        + " |"
    )
    for label, key, precision in (
        ("Planner calls/task", "planner_calls_per_task", 2),
        ("Tool calls/task", "tool_calls_per_task", 2),
        ("USD/task", "cost_per_task_usd", 6),
    ):
        lines.append(
            f"| {label} | "
            + " | ".join("unknown" if s[key] is None else f"{s[key]:.{precision}f}" for s in summaries)
            + " |"
        )
    lines += [
        "",
        "Answer Correctness 和 Grounded Answer Rate 的分母为全部可回答任务，包含拒答及异常；Task Success 还要求工具/澄清正确。Planner 交接优化保留 ACL 和 Strict/all；中间优化轮 P50/成本下降，但最终版本 P50/P95 均未优于基线。每轮独立生成，存在随机性，不能把差异全部归因于交接优化。",
        "",
        "[基线](reports/agent-hardening/evaluation-baseline-live.md) · [失败的首次优化](reports/agent-hardening/latency-first-attempt.md) · [交接优化对照](reports/agent-hardening/latency-comparison.md) · [最终性能对照](reports/agent-hardening/latency-final-comparison.md) · [最终逐题报告](reports/agent-hardening/evaluation-final-quoted-live.md) · [评估协议](docs/agent-evaluation.md)。费用按配置单价估算，排除索引和离线 Judge；中断运行保留，未捕获用量不能计为零。",
        "",
        "最终仍有两题继续追问、三题因自由改写工具计算被保守证据门槛拦截。Clarification Accuracy 只检查是否需要/发生追问，不衡量追问内容质量；自动依据评分也不是人工正确性保证。失败原文、模型输出与判定均保留。",
        "",
        f"最终代码 CI：[{ci['conclusion']}]({ci['html_url']})，版本 `{ci['head_sha'][:7]}`。测试数量不在 README 写死，见[自动生成的完整测试报告](reports/agent-hardening/ci-final/tests.md)与[Docker 验收](reports/agent-hardening/ci-final/container-persistence.json)。",
        "",
        "运行使用一个 worker；Agent 会话仅在内存，15 分钟绝对期限，每用户最多 4 个、全进程最多 100 个活跃任务，重启后需重新开始。当前只有只读工具。制度结论必须引用状态/日期适用的文档；未分类文档需先确认政策状态。完整限制与取消行为见[运行边界](docs/agent-runtime.md)，全部修改、失败与测试见[Modification Report](docs/agent-hardening-report.md)。",
        end,
    ]
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    section = "\n".join(lines)
    if start in text:
        a, b = text.index(start), text.index(end) + len(end)
        text = text[:a] + section + text[b:]
    else:
        text = text.replace("<!-- V3_RESULTS_START -->", section + "\n\n<!-- V3_RESULTS_START -->")
    readme.write_text(text, encoding="utf-8")
    print("README Agent results regenerated from complete saved reports")


if __name__ == "__main__":
    main()
