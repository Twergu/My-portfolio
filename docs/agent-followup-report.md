# 计算断言、澄清与人工审核修改报告

本轮对应三项优先级。上一轮 [Modification Report](agent-hardening-report.md)、24 题 JSON、三项计算误拒答和两项澄清失败均保留，不改标签或删样本。

## 1. 计算类 Claim 由服务器渲染

Generator 可在 `claims` 中返回 `{"calculation_source_id": 4}`。这只是对当前服务器工具来源的引用；不能附带 text、evidence、结果、单位覆盖或自报 Claim 类型。后端验证来源存在、属于 Calculator/Calendar、具有 observation_id 和结构化结果，再生成固定的中日英文本和引用。文档或用户来源编号不能冒充工具。

Calculator 保留原始十进制字符串、运算、结果、舍入信息和可选单位；显示前重新计算，使用同一个十进制实现。单位标签只接受枚举，必须能在当前授权文档或用户输入中找到带相应操作数的原文，后端固定引用该出处；未提供单位时保留为空，不猜测或自动换算。字面单位绑定不证明量纲和业务适用性，这些仍需 Strict 验证。

Calendar 保留开始/结束日期、基准日期、时区、首尾包含规则、工作周/假日配置及 Mock/live 来源。API 的计算 Claim 另带 `rendering=server_calculation` 和 `calculation` 结构，保存工具、observation_id、来源编号、原始参数、结果和单位出处。自由文本中的业务许可/资格/审批结论仍须有适用 Document Evidence；所有计算和政策 Claim 均执行 Strict/all。没有放宽精确引语匹配，也不接受模型声明“非 Policy”绕过。

涉及 `backend/calculations.py`、`agent_tools.py`、`agent_grounding.py`、`agent_service.py`、`rag.py`、`verification.py`。`tests/test_agent_calculations.py` 覆盖三语言、两种工具、单位替换、伪造 ID/结果/类型、夹带审批、Verifier 否定时隐藏、以及三项原始失败的受控合同回归。只把原候选的计算项换成结构化引用，不改历史报告或其他断言。该受控测试不是新的真实 API 成绩。

首项相关回归：98 passed、24 PostgreSQL skipped；数据库测试在真实 CI 单独验收，不能把本地跳过算作通过。

后续真实运行又发现一项语义误拒答：服务器只写“2026-10-09 加七个日历日为 2026-10-16”，Verifier 却将它读成公司返还期限，要求提供制度条文。后端现在将经过结构化结果验证的 `rendering=server_calculation` 标记传给 Verifier；模型无法提交这个字段。Verifier 仍须验证运算、日期、单位及限制，但不能给纯计算凭空添加制度含义。自由文本制度推论仍需文档，标记不能覆盖矛盾内容，否定 verdict 仍使回答隐藏。新增伪造标记及正反例回归。

## 2. Clarification 的完整性

`backend/clarification.py` 生成逐字问答上下文：原始目标、每轮自述及它对应的前序问题。Planner 与 Generator 使用同一份内容，不把最新回复当成新任务，也不因“回复过”就默认全部字段已解决。Generator 同时接收服务器确定的政策适用日期；文档生效日期不再被提示成额外个人条件。

共享协议区分当前任务与后续办理：条件/材料说明不必先证明雇主已经确认；单课程估算无需总课程数；用户请求总额时缺少数量仍需追问。全职不等于非承包商，允许给出带明确排除条件的申请规则说明，不能伪称身份或批准已被确认。真实冲突或确实缺少的决定性条件仍可追问。

两个冻结日文案例的回归验证多轮原文与目标完整地进入 Planner/Generator；另覆盖总额仍需数量和冲突信息不能自动确认。语义上是否仍需追问取决于模型，以上是上下文与提示合同，不宣称确定性自然语言理解。

相关回归：63 passed、3 PostgreSQL skipped。随后真实运行发现 Generator 同时返回 answered/claims 和 questions，违反原有互斥状态合同。新增一次有上限的模型格式修复；不静默删除问题/断言、不重试已经被 quote/provenance/Verifier 拒绝的答案。修复后仍执行全部 Strict 检查，重复无效输出继续隐藏。新增三个正反例验证次数上限及 Verifier 拒绝仍生效。

最终本地完整回归为 313 passed、37 PostgreSQL skipped；跳过不计通过。Ruff 检查及格式检查通过。真实 API 与 CI 最终结果见下方。

## 3. 人工审核集

准备 [8 例审核包](agent-human-review-v1.md)、`evals/agent-human-review-v1.json` 和空白 annotations。含真实“每笔最多 5000 日元”错误候选；5,001 与恰好 5,000 的边界；计算不等于许可；原文收据时点歧义；日文附条件解释和课程估算；Mock 日历不能证明审批。

每例提供问题、完整政策原文、候选、必要证据/允许解释范围和需要审核的参考答案。**已由本对话用户实际审核 8/8**；首次“是”的回复存在歧义，确认后用户逐题写明政策解释，原始文字、标签映射及时间存入[annotations](../evals/agent-human-review-v1.annotations.json)。H01/H03/H04/H08 的候选错误且无据，H02/H05/H06/H07 正确且有据；拟定参考答案获认可。[审核报告](../reports/agent-followup/human-review-completed.json)与此前待审核快照分别保存。审核人看到了参考答案，这是辅助审核，不是独立盲评。

`scripts.human_review_report` 校验冻结数据摘要、审核人声明、带时区时间、全部案例唯一且完整。未签署或缺项不给人工准确率；参考答案不被认可时保留“待裁决”，不将其算作已验收真值。实际审核后的 H01 标签可与旧 Verifier 的 supported=true 比较。脚本只能记录审核人声明，不能技术核实其身份。八例含故意错误的候选，其正确率是候选校准结果，不是一次新的 Agent 任务成功率。

`tests/test_agent_human_review.py` 覆盖未审核/未签署、字符串布尔值、部分审核、摘要变更、重复 ID、时间格式、不同意参考答案和历史自动判定分歧。自动测试使用显式测试签署者；真实标注仅来源于用户本次逐题回复。

基于确认的语义，在 Generator/Verifier 提示中加入通用规则：如果更高数值存在另一条审批路径，不得把分界值表述为绝对上限；真实报销上限仍按原文保留。没有硬编码 5,000 的业务规则或放宽验证。`scripts.agent_human_calibration` 调用真实 Verifier 对八个人工样本逐条校准：[结果](../reports/agent-followup/human-verifier-live.json)为 **7/8 一致、Precision 1.00、Recall 0.75，0 API 错误**。H01 绝对上限误述现被拒绝，H05“收据时点有操作歧义”的说明仍被模型判无据而与人工不同。该样本已用于开发新提示，属于开发集校准，不能宣称是未见数据上的准确率。

## 实测与剩余限制

[第一轮五个旧失败场景](../reports/agent-followup/five-cases-live.md)实际调用 Embedding、Planner、Generator、Strict Verifier 和独立 Judge：3/5 成功。课程估算、Mock 日历、跨政策计算完成；采购中服务器计算 Claim 已通过，但另一个政策适用性推论被拒绝；通勤仍被追问政策日期/雇佣类别。保留全部失败并补充日期上下文及附条件适用性说明。

完整 [24 题实测](../reports/agent-followup/full-live.json)在最后的格式修复/审批门槛提示加入**之前**完成：自动 Task Success 19/24，Correctness 13/18，Grounded Answer Rate 15/18，交付 15 个回答，三个原计算失败场景均完成。P50/P95 为 10.357/20.126 秒，估算 USD 0.002460/task，排除索引与 Judge；[同集对照](../reports/agent-followup/full-comparison.md)保留全部失败。自动“正确”中采购题再次把分界写成上限，与用户确认的政策解释冲突，因此这些分数不是人工准确率；不改动原自动评分。这一轮另有输出状态混合、必要引用缺失、再次追问及 Judge 对完整性的争议。

格式修复后[五题再次实测](../reports/agent-followup/five-cases-final-live.json)：交付 4/5，四个交付均通过独立正确性/依据检查，但冻结 Task Success 仍为 3/5。通勤题直接正确说明申请条件，没有多余追问，按旧“必须澄清”标签仍计失败，不调整旧标签；跨政策题的纯日期计算被 Verifier 误读成制度期限而拒绝。该计算文本明确限定为计算、不构成业务许可，因此这是 Verifier 误拒答；是否完整解释 RET-26 七日规则应另作回答完整性检查。原始判定继续保留。

最后的[真实 Verifier 回放](../reports/agent-followup/calculation-verifier-replay.json)保留该失败候选的全部原文和证据，仅为后端重新验证过的计算引用加入服务器标记：四条断言全部通过；另设的“计算即公司期限且用户已合规”反例仍被拒绝。`python -m scripts.agent_calculation_replay --live --output <new-path.json>` 可复现，保存原始输入、输出和用量。两个请求分别耗时 8.800 / 2.744 秒，配置单价估算共 USD 0.001640；这只是 Verifier 回放，不能作为整条 Agent 的延迟。此回放包含最终提示修复；24 题、五题和人工校准分别对应先前开发阶段，不能拼成最新版本的一轮全量成功结果。

真实 PostgreSQL/Docker CI 正在进行。工作日日历仍为 Mock；ACL、Citation、Strict 均保留。语义推论、澄清必要性和单位/类别适用性仍依赖模型；缺失引用仍会拒答，人工集也只有八例且不是盲评。既有 24 题属于冻结合成回归集，对“解释条件是否必须追问”的标注边界应另行审核新版本，不能改写旧成绩。
