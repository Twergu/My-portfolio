# Agent 可靠性与评估修改报告

按用户给定顺序实施，每项先测试再进入下一项。真实模型报告与受控回归测试分开记录；历史失败数据保留。

## P0-1 日文多轮回答

完成。第三阶段原始失败只保留了界面和用量，未捕获未展示的候选，不能事后声称恢复了原来的四条断言。使用同一日文问题、补充信息和虚构政策重新实际运行，第一次复现 2/4 通过，第二次 3/3 通过；完整[修复前请求、Generator、证据与 Verdict](../reports/agent-hardening/p0-before-live.json)保留，原第三阶段 1/4 记录亦保留。

确认原因：

1. Generator 的“满足条件”断言只引用用户输入，未在同一断言引用制度，也未明确限定最终资格待确认。该拦截合理，不能让 Verifier 从其他断言借用未引用的政策。
2. 对“申請には…を提出します”的办理说明，Verifier 将其理解成用户实际/必定提交，将“可以提交”不等于“已经提交”用于否定政策要求，出现日文规范性表述的误判。

修改 `backend/rag.py`、`backend/verification.py`：生成提示明确每条资格推论联合引用制度和用户条件，并同句保留自述及待确认限定；必要材料使用“提出が必要です”等规范性表述。Verifier 区分办理要求、用户能力与已执行事实，仍拒绝无制度引用的资格结论、未证实提交、批准或承诺。

验证：

- [修复后完整真实多轮](../reports/agent-hardening/p0-after-live.json)：两次均 needs_input → answered，均 3/3 断言通过。
- [真实 Verifier 回放](../reports/agent-hardening/p0-verifier-replay.json)：六个正反例均符合预期；明确区分记录原句与人工构造的对照，不把回放当成完整 Agent 运行。
- `tests/test_agent_japanese_regression.py` 使用[冻结的真实失败](../evals/agent-ja-regression.json)作确定性回归，验证提示合同、仅传被引用证据、严格校验与未验证结果隐藏。该测试使用受控模型返回，不能替代真实 API 测试。
- 相关 Grounding/Agent 测试：62 passed、1 PostgreSQL skipped（下一项真实环境执行）；Strict 始终强制 all，没有关闭验证或接受缺失依据。

脚本：`python -m scripts.agent_diagnose --live --repeats 2 --output <new-report.json>`，`python -m scripts.agent_verifier_replay --live --output <new-report.json>`。原始诊断仅在显式离线脚本对虚构政策启用，不在生产 HTTP 日志中记录私有问题或密钥。额外保留最初沙箱临时目录错误的 `p0-before.json`。

限制：小样本通过不是稳定准确率保证；提示修复不能给出形式化语义保证，后续 Agent Evaluation 将保留失败统计。

## P0-2 完整 CI / PostgreSQL / Docker

完成。[GitHub Actions 37181289264](https://github.com/Twergu/My-portfolio/actions/runs/37181289264) 在提交 `4e1902bdf49541275cedeaf74c38258f856d9604` 全绿：248 passed、0 failed、0 errors、0 skipped。真实 PostgreSQL 17 + pgvector 服务执行数据库用例，Agent HTTP/ACL/多轮集成测试同时覆盖 SQLite 与 PostgreSQL。

修改 `tests/test_agent_integration.py` 复用双数据库 fixture；`scripts/container_smoke.py` 增加容器内 Agent API 和前端可用性检查。Docker Compose 构建、健康、PDF 上传索引/下载、重启后的持久化均通过。容器 Smoke 使用本地检索模式检查 Agent 的 API 配置门禁，不伪称调用真实模型；真实模型证据见 P0-1。CI 仍要求任何 skipped 导致失败。后续修改会再跑最终完整 CI。

## P1-3 Agent Evaluation

完成。新增 `evals/make_agent.py`、`evals/agent_dataset.json`、`evals/agent_metrics.py`、`scripts/agent_evaluate.py` 与 `docs/agent-evaluation.md`，扩展 `evals/judge.py` 的 Agent 证据语义。24 个独立中日英场景，规划和最终回答分开评分，保留每次原始模型输出及失败，每题保存 JSON/Markdown，禁止覆盖已有报告。

对应 `tests/test_agent_evaluation.py` 与既有 Evaluation 测试共 21 passed。评分验证覆盖拒答/异常分母、未交付与已交付 groundedness、续接累计 trace 防重复计数、未知成本保持 null、数据集可重建。最初沙箱临时目录失败保留在 `evaluation-baseline.json`，不计作模型质量实验。

[真实基线](../reports/agent-hardening/evaluation-baseline-live.md)：24/24 完成，Task Success 50.0%，Planning Success 87.5%，Tool Selection 91.7%，Clarification 95.8%；18 个可回答任务中交付 7 个，独立 Correctness/Groundedness 均通过，其余计为失败。P50/P95 12.259/18.122 秒，USD 0.002236/task（排除 Judge 与索引）。失败包括不连续 quote、无文档支持的额外限定、错误自述归因及多余追问。这是回归集，包含歧义问题且未经人工审核，不宣称是泛化准确率或已稳定上线。

## P1-4 Latency

实施中。基线平均每任务 Planner 4.726 秒、Generator 3.608 秒、Verifier 2.394 秒、Knowledge Search 0.221 秒。`backend/agent.py` 新增可选 `answer_after`：最后一次只读工具成功且提供非空文本/来源后可直接交给 Generator；省去只负责 `prepare_answer` 的模型往返。空结果、失败和重复调用均不能走捷径，保留全部成功前提，并由 AgentService 再次 ACL 检查与 Strict/all 验证。

新增编排与双数据库 HTTP 安全回归，本地相关测试通过（数据库用例在最终 CI 实际执行）。[第一轮对照](../reports/agent-hardening/latency-first-attempt.md)保存了未达到目标的优化：Planner 次数 2.67→2.00，P50 12.259→10.997 秒，但 P95 18.122→20.132 秒、Task Success 50.0%→45.8%。不将此报告当作最终成功。

确认其中一例 business_task 检索直接交接而未进行 Calculator，故在后端增加限制：业务知识检索必须再规划；只有直接知识问答，或已经有制度前提的最终 Calculator/Calendar 调用可以提前交接。新增防过早交接测试与中途权限撤销测试。收紧后的相关测试 83 passed、18 PostgreSQL skipped；同一 24 题再次实测中，保留第一次失败运行。

## P2-5 Policy Claim 约束

待执行。

## P3-6 State 边界

待执行。
