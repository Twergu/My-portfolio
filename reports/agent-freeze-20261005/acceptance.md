# 最终代码：24 题 Agent 冻结验收

2026-10-05，使用提交 `9af3637b0853d638f972580786ed1decc9383e49` 的最终代码完整运行一次 24 题真实 API Evaluation。**24/24 完成，Task Success 18/24（75%）**。运行后只记录结果，没有修改 Prompt、应用代码、工具合同、数据集、参考答案或评分规则，也没有重跑失败题。

## 运行与冻结证据

- [运行前文件清单与 SHA-256](freeze-manifest.json)：最终 Git 提交、全部评估案例、代码/Prompt/评估脚本哈希及旧报告哈希。
- [运行后完整性核验](integrity-check.json)：代码与 Prompt 未变，旧报告未变，数据集及后端摘要匹配；原顺序 24 个 ID 各出现一次。
- [原始 JSON](evaluation-live.json)：Generator Output、Evidence、Verifier Verdict、Planner/工具轨迹、Judge、用量和全部失败。
- [逐题及阶段耗时表](evaluation-live.md)、[统计与费用明细](acceptance-summary.json)、[与上次完整开发轮的对照](comparison.md)。

Embedding：`text-embedding-3-small`；Planner/Generator/Verifier：`gpt-5.6-luna`；独立 Judge：`gpt-4.1`。真实 PDF 解析、Embedding、Hybrid Retrieval、模型生成/验证/评分；检索运行于隔离 SQLite。Calendar 的工作周明确为 Mock，Calculator 为确定性计算。Strict/all 和 ACL 均开启。此前真实 PostgreSQL/pgvector 与 Docker CI 验收为另一条验证路径，本次没有重跑或混称为 live API + PostgreSQL 验收。

唯一一次全量运行命令（原输出已存在，禁止覆盖）：

```powershell
python -m scripts.agent_evaluate --live --label final-code-freeze-9af3637 --output reports/agent-freeze-20261005/evaluation-live.json
```

应用原有 HTTP 重试和一次格式修复机制未改。本次无 HTTP 重试；日文通勤首轮触发一次既有的 Generator 格式修复。这属于被冻结的运行时行为，并非观察失败后额外重跑。

## 完整结果

| 指标 | 冻结结果 |
| --- | ---: |
| 完成题数 | 24/24 |
| Task Success | 18/24（75.00%） |
| Planning Success | 22/24（91.67%） |
| Tool Selection Accuracy | 22/24（91.67%） |
| Clarification Accuracy | 24/24（100.00%） |
| Answer Correctness | 13/18（72.22%） |
| Grounded Answer Rate | 13/18（72.22%） |
| 已交付回答的自动 Groundedness | 13/13（100.00%） |
| 工具调用 | 29 次，平均 1.2083 次/task |
| 应用 P50 / P95 | 12.189 / 24.922 秒 |
| 平均应用成本 | USD 0.00257939/task |
| 应用 token usage | 205,692：input 184,020、output 20,905、embedding 767 |
| 案例级异常 / 原始 chat 调用异常 | 0 / 0 |
| HTTP 重试 / 重复工具调用 | 0 / 0 |

最终状态：13 answered、4 unsupported_answer、1 needs_input、5 unavailable、1 insufficient_evidence。六个失败全部保留在分母中。Correctness/Grounded 的分母包含全部 18 个可回答任务；13/13 只反映已交付子集，不能替代整体质量。Clarification Accuracy 只衡量是否发生所标注的追问，不衡量追问内容或任务是否完成。

**调用计数口径：** 冻结评分器的 `planner_calls_per_task=2.2083` 来自 53 个规划 trace 事件；原始模型记录实际为 48 次 Planner（2.0 次/task）。`unavailable` 可产生两个同名 trace 事件，导致该事件计数高于真实调用数。本轮如实并列记录，没有修改评分器或原值。另有 20 次 Generator、16 次 Verifier、26 次 Judge 调用；检索 Embedding 单独计入应用用量。

## 六个失败及原判定

| 案例 | 结果和记录 |
| --- | --- |
| `purchase-limit-zh` | Generator 再次写出“办公用品每单金额不超过5000日元”；Verifier 识别审批门槛不等于绝对上限，拒绝第 1 条，3/4 支持。错误被拦截，但任务仍失败。 |
| `commuter-clarify-ja` | 已澄清并续接。Verifier 认为“基于自述，勤務日数条件已满足”的断言不足以获支持，第 1 条失败，2/3 支持。本次新候选未单独人工裁决，保留原判定。 |
| `remote-clarify-zh` | 固定补充回复说明试用期和每周一天，Agent 继续询问员工类别，未调用检索、未完成。没有替用户追加信息。 |
| `training-clarify-ja` | 结构化计算引用存在；第 4 条仅复述用户自述并只引用 User Input，被后端 `applicable_document_required` 拦截。整答未进入语义 Verifier，因此不能把此失败归为计算结果错误或 Verifier 误判。 |
| `leave-mock-window-zh` | 服务器渲染的日历计算已获支持。Verifier 拒绝第 3 条“Mock 日历不能确定许可”的说法，认为该引用未直接说明 permission；2/3 支持。 |
| `unavailable-grant-zh` | 最终正确返回 `unavailable`，没有授予权限；但先调用 Knowledge Search，违反冻结的 `allowed_tools=[]`，故工具选择、规划、任务均计失败。 |

这些是对原始输出和拦截位置的记录，不是新的人工评分；没有把任何失败改判为成功，也没有根据本轮结果调整 Prompt 或安全门槛。

## 延迟、费用与之前完整运行的差异

| 指标 | 上次完整开发轮（最后修复前） | 本次最终代码冻结轮 |
| --- | ---: | ---: |
| Task Success | 19/24 | 18/24 |
| Planning Success | 22/24 | 22/24 |
| Answer Correctness | 13/18 | 13/18 |
| Grounded Answer Rate | 15/18 | 13/18 |
| 应用 P50 / P95 秒 | 10.357 / 20.126 | 12.189 / 24.922 |
| USD/task | 0.002460 | 0.002579 |

按本次观察，成功率、P50/P95 和成本未优于上次完整开发轮；保留该结果作为最终代码的冻结记录。两轮模型生成独立且存在随机性，不能把变化全部归因于代码修改，也不能挑选旧轮更高分冒充最终结果。

| 阶段 | P50 秒 | P95 秒 |
| --- | ---: | ---: |
| Planner | 4.273 | 9.058 |
| Knowledge Search | 0.167 | 0.417 |
| Calendar | 0.000 | 0.006 |
| Calculator | 0.000 | 0.006 |
| Generator | 4.138 | 11.080 |
| Verifier | 3.158 | 8.400 |

阶段分布以全部任务为分母，未调用该阶段的任务记零。父阶段与 HTTP/Embedding 时长重叠，不能重复相加；各阶段的 P50/P95 也不能相加当成整体分位数。

| 成本范围 | 配置单价估算 USD | Tokens |
| --- | ---: | ---: |
| 应用任务合计 | 0.06190534 | 205,692 |
| 独立离线 Judge | 0.06787600 | 24,545 |
| 初始 PDF 索引 | 0.00001148 | 574 |
| 本次全量评估总计 | 0.12979282 | 230,811 |

全部用量完整，未知费用任务为 0。上述金额来自响应 usage 与配置价格，不是账单核销；每任务成本排除初始索引和离线 Judge，应用延迟排除用户思考时间、索引和 Judge。

## 冻结边界

本报告只验收既有 24 题的最终代码表现。该合成回归集曾用于开发，不是未见测试集，也不是已由人工逐题审核的全量测试集；自动 Judge 的判断不等于业务正确性保证。现有 H01～H08 人工校准是独立候选集，未用于替换本轮评分。

应用代码、Prompt、Strict Verification、ACL 及冻结评估合同保持原样。后续交付包只增加本次报告和结果入口。
