# Agent Evaluation 协议

`evals/agent_dataset.json` 是冻结的 24 个虚构企业任务（中、日、英），通过 `python -m evals.make_agent` 重建。包含制度问答、缺少个人条件的多轮澄清、跨文档计算/日期、缺少写工具、无政策、缺少实际日历等情况。数据和参考答案由 AI 编写，**尚未人工审核**，不代表生产准确率。

运行前在 `.env` 配置现有 API 及独立 `RAG_EVAL_JUDGE_MODEL`。执行：

```powershell
python -m scripts.agent_evaluate --live --label baseline --output reports/agent-hardening/evaluation-baseline-live.json
```

选择一个新的报告文件名；程序拒绝覆盖旧实验。运行使用隔离临时库，经真实 PDF 解析、真实 Embedding、SQLite Hybrid Retrieval、真实 Planner/Generator/Strict Verifier；Calculator 为确定性十进制计算，Calendar 明确是 Mock 工作周。权限在搜索之前应用，模型无法扩大范围。不存在发邮件、提交申请等写操作。生产 PostgreSQL/pgvector 行为由独立 CI 验收，不把本脚本的 SQLite 运行称为 PostgreSQL 性能测试。

每个场景有独立任务状态，可最多补充一次预先写好的用户答复，避免评估器临时替模型补全条件。24 个结果均保留；错误、被拦截、继续追问未完成，全部计入失败。每题后保存 JSON 和 Markdown；中断报告注明 completed/expected，不能当作完整结果。原日文失败仍在 `agent-ja-regression.json` 和早期诊断中保留，本集合也包含该多轮问题。

## 指标

- **Tool Selection Accuracy**：实际尝试的工具集合包含 required 且不超 allowed，且不存在工具错误。重复/非法调用不能当作正确选择。
- **Clarification Accuracy**：实际是否追问，与标注的必须追问一致。参考答复只在实际追问时给出。
- **Planning Success**：工具与澄清均正确，且可回答题实际到达 ready；无答案题到达允许的 unavailable/insufficient_evidence。该分数不依赖最终 Generator 是否成功。
- **Task Success**：Planning Success，加正确终态；可回答题还要求独立 Judge Correctness、每条引用 Groundedness 和运行时 Strict 全部通过。
- **Answer Correctness / Grounded Answer Rate**：分母为全部可回答任务，含误拒答和异常。另报 grounded_rate_among_delivered，明确仅对已交付答案计算，不能代替整体成功率。
- **Tool Calls / Planner Calls**：最终累计 trace 计数，澄清前后不重复相加。
- **Latency**：将每次 API 输入的应用耗时相加，排除用户思考、索引和离线 Judge；同时保留单阶段 Planner、Knowledge Search、Calendar、Calculator、Generator、Verifier 耗时。搜索含 Embedding，阶段与 HTTP 耗时不能重复相加。
- **Cost**：按响应 token usage 和配置单价估算应用每任务成本；索引、Judge 单列。无法确定的成本保持 null，不能算成零。

独立 Judge 两次调用分别评估正确性和引用：正确性可见参考答案/必要文档；引用 Judge 只能见候选及其实际引用，不能从 gold 借用缺失证据。两者均看不到运行时 Verifier verdict。自动 Judge 仍可能误判，失败需结合原文审查。

离线脚本记录 Generator Output、Evidence、Verifier Verdict 和所有模型请求文本，只用于虚构数据诊断；不要用该明文诊断脚本处理私有生产数据。测试中的受控返回只验证评分及工程合同，不冒充真实 API 结果。
