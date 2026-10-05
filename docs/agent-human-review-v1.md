# Agent 小规模人工审核包

状态：**已由本对话用户审核，8/8**。用户逐题意见与时间保存在[签署标注](../evals/agent-human-review-v1.annotations.json)，结果见[审核报告](../reports/agent-followup/human-review-completed.json)。候选和拟定参考答案由 AI 准备，审核人看到了参考答案，因此是辅助审核，不是独立盲评；以下保留原始审核材料。

逐题记录：候选正确 / 全部断言有据 / 是否认可拟定参考答案，均填 是或否；不确定请写原因并暂不签署。审核人可用昵称。最终标注绑定冻结数据摘要，不修改以前的评估结果。

可在聊天中回复：`审核人：昵称；H01：否/否/是；H02：是/是/是；...`，并注明需要修订的题目。这里的格式示例不是已通过审核的标签。

## H01

**问题：** 采购办公用品是否每笔最多只能购买 5,000 日元？

**原文（agent-eval-policies.pdf 第 1 页）：**

> PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.

**待评候选（真实失败原句）：** 当前办公用品采购政策规定，每笔订单金额上限为5000日元。

**审核要点：** 区分审批路线与绝对禁止；原文另有超过 5,000 的审批路径。

**拟定参考答案（也需要审核）：** 原文未规定绝对采购上限；超过 5,000 JPY 需购买前取得采购部门批准。

审核：候选正确 □是 □否；全部断言有据 □是 □否；参考答案认可 □是 □否；备注：____

## H02

**问题：** 单笔办公用品 5,001 日元应走哪条审批路线？

**原文（agent-eval-policies.pdf 第 1 页）：**

> PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.

**待评候选（新编候选）：** 超过 5,000 日元需在购买前取得采购部门批准；原文没有说超过该金额一律禁止采购。

**审核要点：** 必须保留购买前审批，不得声称已经获批。

**拟定参考答案（也需要审核）：** 5,001 大于 5,000，走采购部门事前批准路径。

审核：候选正确 □是 □否；全部断言有据 □是 □否；参考答案认可 □是 □否；备注：____

## H03

**问题：** 单笔恰好 5,000 日元的审批路线是什么？

**原文（agent-eval-policies.pdf 第 1 页）：**

> PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.

**待评候选（新编候选）：** 恰好 5,000 日元必须取得采购部门批准。

**审核要点：** at most 包含边界值；不得把 above 误解成大于等于。

**拟定参考答案（也需要审核）：** 恰好 5,000 属于 at-most 路线，按原文需要收据和经理确认。

审核：候选正确 □是 □否；全部断言有据 □是 □否；参考答案认可 □是 □否；备注：____

## H04

**问题：** 按每件 1,200 日元估算 3 件办公用品，是否已获采购许可？

**原文（agent-eval-policies.pdf 第 1 页）：**

> PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.

**待评候选（新编候选）：** 3 × 1,200 = 3,600 日元，所以已获得公司采购许可。

**审核要点：** 数学正确不等于审批完成；仍需制度材料/确认。

**拟定参考答案（也需要审核）：** 估算 3,600 日元；计算不构成许可，办理要求应另按 PROC-26 说明。

审核：候选正确 □是 □否；全部断言有据 □是 □否；参考答案认可 □是 □否；备注：____

## H05

**问题：** 请说明采购需要什么材料，原文是否存在措辞疑点？

**原文（agent-eval-policies.pdf 第 1 页）：**

> PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.

**待评候选（新编候选）：** 原文要求收据和经理确认，但把它们放在购买前的措辞有实际操作歧义，应向制度维护人核实，不能自行改写成另一项制度。

**审核要点：** 区分忠实转述与以常识篡改原文；允许明确指出歧义。

**拟定参考答案（也需要审核）：** 保留原文要求，同时标注收据时点歧义供制度维护人确认。

审核：候选正确 □是 □否；全部断言有据 □是 □否；参考答案认可 □是 □否；备注：____

## H06

**问题：** 通勤補助の申請条件を確認したいです。フルタイム勤務で週3日出社し、必要書類は提出できます。

**原文（agent-eval-policies.pdf 第 2 页）：**

> COMM-26 current commuter support policy: Full-time employees working onsite at least three days per week may apply. Contractors are excluded. Required application documents are an employment status declaration and an onsite work schedule. Eligibility is subject to employer confirmation; self-reported employment and attendance alone do not establish approval.

**待评候选（新编候选）：** 自己申告どおりフルタイム従業員として週3日出社し、業務委託ではない場合、申請条件に該当し得ます。業務委託は対象外で、雇用主の確認が必要です。雇用形態申告書と出社勤務スケジュールの提出が必要であり、提出済み・承認済みとは判断できません。

**审核要点：** 不能从全职推出非承包商，也不能把可提交写成已提交；可解释条件而不作最终审批。

**拟定参考答案（也需要审核）：** 按自述作明确附条件说明，保留 contractor 排除、雇主确认和必要材料；不确认身份或批准。

审核：候选正确 □是 □否；全部断言有据 □是 □否；参考答案认可 □是 □否；备注：____

## H07

**问题：** 研修料金は20000円です。中止ではなく、承認ではなく1コースの見積りを知りたいです。

**原文（agent-eval-policies.pdf 第 4 页）：**

> TRAIN-26 current training policy: A course fee is reimbursed at 80 percent, capped at 30000 JPY per course. Manager preapproval and a completion certificate are required. A cancelled course is not reimbursable. The estimate is conditional on document review by Finance.

**待评候选（新编候选）：** 1コースの条件付き見積りは20,000円×80%=16,000円です。30,000円の上限以下ですが、上司の事前承認、修了証明書およびFinanceの書類確認が必要で、支給確定ではありません。

**审核要点：** 单课程估算不需总课程数；不得移除前置要求或保证报销。

**拟定参考答案（也需要审核）：** 单课程条件估算 16,000 JPY，仍需经理事前批准、完成证明及 Finance 审核。

审核：候选正确 □是 □否；全部断言有据 □是 □否；参考答案认可 □是 □否；备注：____

## H08

**问题：** Use a mock Monday-Friday calendar for 2026-10-05 through 2026-10-07. Does that establish official approved leave?

**原文（agent-eval-policies.pdf 第 8 页）：**

> LEAVE-26 current leave procedure: Planned leave requires a leave request form and manager approval before absence. Workday counts depend on the official company calendar. This knowledge base does not contain leave balances or a company holiday calendar; a mock Monday-Friday calendar cannot establish entitlement or official leave days.

**待评候选（新编候选）：** The mock calendar gives three working days, so the company has approved three days of leave.

**审核要点：** Mock 日历不证明正式工作日、剩余额度或审批。

**拟定参考答案（也需要审核）：** 仅可报告 Mock 下三天；正式日历、额度和经理批准不能从计算确定。

审核：候选正确 □是 □否；全部断言有据 □是 □否；参考答案认可 □是 □否；备注：____

## 保存与评分

填写 `evals/agent-human-review-v1.annotations.json` 后运行 `python -m scripts.human_review_report --annotations evals/agent-human-review-v1.annotations.json --output reports/agent-followup/human-review.json`。未签署或缺项不会产生人工准确率；任何参考答案未认可会标记待裁决。脚本不能核验审核人的真实身份，human_attested 是审核流程声明，不是密码学证明。
