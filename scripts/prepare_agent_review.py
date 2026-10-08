"""Prepare eight review candidates; never fabricate human annotations."""

import hashlib
import json

from backend.config import ROOT


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def dataset():
    policies = json.loads((ROOT / "evals/agent_dataset.json").read_text(encoding="utf-8"))["pages"]
    raw = json.loads((ROOT / "reports/agent-hardening/evaluation-final-live.json").read_text(encoding="utf-8"))
    recorded = next(c for c in raw["cases"] if c["id"] == "purchase-limit-zh")
    first = recorded["turns"][-1]["claims"][0]
    rows = [
        (
            "H01",
            "采购办公用品是否每笔最多只能购买 5,000 日元？",
            1,
            first["text"],
            "区分审批路线与绝对禁止；原文另有超过 5,000 的审批路径。",
            "真实失败原句",
            "原文未规定绝对采购上限；超过 5,000 JPY 需购买前取得采购部门批准。",
        ),
        (
            "H02",
            "单笔办公用品 5,001 日元应走哪条审批路线？",
            1,
            "超过 5,000 日元需在购买前取得采购部门批准；原文没有说超过该金额一律禁止采购。",
            "必须保留购买前审批，不得声称已经获批。",
            "新编候选",
            "5,001 大于 5,000，走采购部门事前批准路径。",
        ),
        (
            "H03",
            "单笔恰好 5,000 日元的审批路线是什么？",
            1,
            "恰好 5,000 日元必须取得采购部门批准。",
            "at most 包含边界值；不得把 above 误解成大于等于。",
            "新编候选",
            "恰好 5,000 属于 at-most 路线，按原文需要收据和经理确认。",
        ),
        (
            "H04",
            "按每件 1,200 日元估算 3 件办公用品，是否已获采购许可？",
            1,
            "3 × 1,200 = 3,600 日元，所以已获得公司采购许可。",
            "数学正确不等于审批完成；仍需制度材料/确认。",
            "新编候选",
            "估算 3,600 日元；计算不构成许可，办理要求应另按 PROC-26 说明。",
        ),
        (
            "H05",
            "请说明采购需要什么材料，原文是否存在措辞疑点？",
            1,
            "原文要求收据和经理确认，但把它们放在购买前的措辞有实际操作歧义，应向制度维护人核实，不能自行改写成另一项制度。",
            "区分忠实转述与以常识篡改原文；允许明确指出歧义。",
            "新编候选",
            "保留原文要求，同时标注收据时点歧义供制度维护人确认。",
        ),
        (
            "H06",
            "通勤補助の申請条件を確認したいです。フルタイム勤務で週3日出社し、必要書類は提出できます。",
            2,
            "自己申告どおりフルタイム従業員として週3日出社し、業務委託ではない場合、申請条件に該当し得ます。業務委託は対象外で、雇用主の確認が必要です。雇用形態申告書と出社勤務スケジュールの提出が必要であり、提出済み・承認済みとは判断できません。",
            "不能从全职推出非承包商，也不能把可提交写成已提交；可解释条件而不作最终审批。",
            "新编候选",
            "按自述作明确附条件说明，保留 contractor 排除、雇主确认和必要材料；不确认身份或批准。",
        ),
        (
            "H07",
            "研修料金は20000円です。中止ではなく、承認ではなく1コースの見積りを知りたいです。",
            4,
            "1コースの条件付き見積りは20,000円×80%=16,000円です。30,000円の上限以下ですが、上司の事前承認、修了証明書およびFinanceの書類確認が必要で、支給確定ではありません。",
            "单课程估算不需总课程数；不得移除前置要求或保证报销。",
            "新编候选",
            "单课程条件估算 16,000 JPY，仍需经理事前批准、完成证明及 Finance 审核。",
        ),
        (
            "H08",
            "Use a mock Monday-Friday calendar for 2026-10-05 through 2026-10-07. Does that establish official approved leave?",
            8,
            "The mock calendar gives three working days, so the company has approved three days of leave.",
            "Mock 日历不证明正式工作日、剩余额度或审批。",
            "新编候选",
            "仅可报告 Mock 下三天；正式日历、额度和经理批准不能从计算确定。",
        ),
    ]
    return {
        "id": "agent-human-review-v1",
        "status": "awaiting_human_review",
        "scope": "Eight AI-prepared candidates, one recorded failure. NOT human-reviewed until a real reviewer submits annotations. Fictional policy excerpts; no legal/HR advice.",
        "cases": [
            {
                "id": id,
                "question": q,
                "page": page,
                "document": "agent-eval-policies.pdf",
                "source": policies[page - 1],
                "candidate": answer,
                "review_focus": focus,
                "candidate_origin": origin,
                "proposed_reference": reference,
            }
            for id, q, page, answer, focus, origin, reference in rows
        ],
        "frozen_failure": {
            "report": "reports/agent-hardening/evaluation-final-live.json",
            "case_id": recorded["id"],
            "claim_index": 1,
            "runtime_supported": True,
            "judge_supported": True,
        },
    }


def main():
    data = dataset()
    target = ROOT / "evals/agent-human-review-v1.json"
    template = ROOT / "evals/agent-human-review-v1.annotations.json"
    if target.exists() or template.exists():
        raise SystemExit("Preserve existing review candidates and annotations; use a new version")
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    form = {
        "dataset_sha256": fingerprint(data),
        "reviewer": None,
        "reviewed_at": None,
        "human_attested": False,
        "cases": [
            {
                "id": row["id"],
                "answer_correct": None,
                "all_claims_supported": None,
                "reference_approved": None,
                "notes": "",
            }
            for row in data["cases"]
        ],
    }
    template.write_text(json.dumps(form, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Agent 小规模人工审核包",
        "",
        "状态：**待人工审核，0/8**。此文件和参考答案由 AI 准备，不能算人工标注。请先独立读原文与候选，再检查参考答案。",
        "",
        "逐题记录：候选正确 / 全部断言有据 / 是否认可拟定参考答案，均填 是或否；不确定请写原因并暂不签署。审核人可用昵称。最终标注绑定冻结数据摘要，不修改以前的评估结果。",
        "",
        "可在聊天中回复：`审核人：昵称；H01：否/否/是；H02：是/是/是；...`，并注明需要修订的题目。这里的格式示例不是已通过审核的标签。",
        "",
    ]
    for row in data["cases"]:
        lines += [
            f"## {row['id']}",
            "",
            f"**问题：** {row['question']}",
            "",
            f"**原文（{row['document']} 第 {row['page']} 页）：**",
            "",
            "> " + row["source"],
            "",
            f"**待评候选（{row['candidate_origin']}）：** {row['candidate']}",
            "",
            f"**审核要点：** {row['review_focus']}",
            "",
            f"**拟定参考答案（也需要审核）：** {row['proposed_reference']}",
            "",
            "审核：候选正确 □是 □否；全部断言有据 □是 □否；参考答案认可 □是 □否；备注：____",
            "",
        ]
    lines += [
        "## 保存与评分",
        "",
        "填写 `evals/agent-human-review-v1.annotations.json` 后运行 `python -m scripts.human_review_report --annotations evals/agent-human-review-v1.annotations.json --output reports/agent-followup/human-review.json`。未签署或缺项不会产生人工准确率；任何参考答案未认可会标记待裁决。脚本不能核验审核人的真实身份，human_attested 是审核流程声明，不是密码学证明。",
        "",
    ]
    (ROOT / "docs/agent-human-review-v1.md").write_text("\n".join(lines), encoding="utf-8")
    print("Prepared 8 cases with empty human annotations")


if __name__ == "__main__":
    main()
