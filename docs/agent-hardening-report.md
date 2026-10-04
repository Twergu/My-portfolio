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

执行中。

## P1-3 Agent Evaluation

待执行。

## P1-4 Latency

待执行。

## P2-5 Policy Claim 约束

待执行。

## P3-6 State 边界

待执行。
