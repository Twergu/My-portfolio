# Agent 第二阶段：实际工具与有依据的结果

历史阶段状态：后端工具、Agent API、多轮任务与结果验证已接通；四个真实模型流程检查通过。本阶段交付时暂停，随后获用户继续授权；当前已完成[第三阶段页面接入](agent-stage3.md)。以下保留第二阶段当时的验证范围与结果。

## 修改与效果

| 修改 | 现在的行为 |
| --- | --- |
| Knowledge Search | 调用现有 Dense/Hybrid/Reranker 检索配置，返回真实片段、物理页码、PDF 链接和政策元数据。只允许模型提供查询词；文档范围、ACL 和版本过滤由服务器确定。 |
| Calendar | 支持日期偏移、指定周的星期、包含首尾的日期区间。默认工作日配置明确标为模拟的周一至周五日历，未配置法定/公司节假日；不能查询余额、空闲时间或批准申请。 |
| Calculator | 用 Decimal 执行加、减、乘、除、百分比，禁止执行表达式或代码。最多保留六位小数，明确记录舍入；数值和单位是否适用于业务仍需核对用户/文档依据。 |
| 证据来源 | 区分 `document`、`tool`、`user`。PDF 保留页码链接；工具和用户信息不伪装成 PDF 引用，分别携带计算来源、模拟标记或自述标记。 |
| 回答生成 | 将已检索证据交给共享 `answer_from_sources`，不再次 Embedding/检索。结合政策、计算和用户条件输出结论、材料、步骤。 |
| 严格验证 | Agent 强制 `strict + all`，检查引用编号、原文摘录与全部断言依据；原有 RAG 的 off/fast/strict 设置不变。任何断言不支持则隐藏候选回答。 |
| 双重追问机会 | Planner 可以追问；即便它提前交接，回答阶段发现缺少必要个人条件也可返回 `needs_input`。补充信息后继续原任务，缺政策证据则仍明确拒答。 |
| 多轮与权限 | 状态只存在服务器内存，任务 ID 随机生成并绑定用户。每次模型操作前重新认证和核对范围，回复时重新核对权限、文档、配置及旧证据。范围变化时要求重开任务。 |
| 生命周期 | 最多 100 个活跃任务、每用户 4 个；任务创建后 15 分钟过期，同一任务不能并发回复。只保留等待补充的任务；完成/失败即释放，可显式取消等待中的任务。 |
| 可观测性 | 记录 Planner、Embedding、Generator、Verifier、工具耗时及 token/cost。每次输入单独计时，不把用户思考时间算成模型响应延迟。 |

代码：[实际工具](../backend/agent_tools.py)、[任务与 HTTP 接口](../backend/agent_service.py)、[共享回答链](../backend/rag.py)、[依据验证规则](../backend/verification.py)、[集成测试](../tests/test_agent_integration.py)。

## 接口

通过原有登录 Cookie 或 Bearer Token 认证；local 模式仍是已有的单用户开发模式。

```http
POST /api/agent
Content-Type: application/json

{
  "question": "购买3本办公笔记本，每本1200日元，按采购规定需要提交什么？",
  "language": "zh",
  "document_ids": [],
  "filters": {"policy_status": ["current"]}
}
```

返回 `needs_input` 时携带 `task_id` 与 `questions`。继续任务使用 `POST /api/agent/{task_id}/reply`，正文仅为 `{"question":"用户补充的信息"}`；不能在回复中上传状态、修改文档范围或伪造工具结果。取消等待中的任务使用 `DELETE /api/agent/{task_id}`。

`answered` 携带已验证的 `claims`、`sources`、`support`、`trace` 和 `metrics`。`evidence_notices` 指明模拟数据、自述信息及本系统未执行外部业务操作。其他状态包括 `needs_input`、`insufficient_evidence`、`unsupported_answer`、`unavailable`、`error` 和 `limit_reached`。

当前时区为 Asia/Tokyo，参考日期由服务器在任务开始时确定并保持不变，响应会明确返回。无任何有权限且索引有效的文档时，先返回 `no_accessible_evidence`，不调用模型；当前 Agent 入口定位于企业知识任务，尚未开放空知识库下的独立计算模式。

## 真实 API 验证

[完整 JSON 报告](../reports/agent-stage2/live-smoke.json) 记录实际请求、用量、响应、验证结果和费用。本次使用配置中的 gpt-5.6-luna 与 text-embedding-3-small，通过临时应用上传虚构 PDF 并真正完成索引；检索使用隔离的 SQLite + Hybrid，日期与计算工具实际执行。

| 场景 | 实际结果 |
| --- | --- |
| 中文采购 | 知识检索 + Calculator：3 × 1200 = 3600 日元，列出采购材料并引用原文。 |
| 日文培训申请 | 知识检索 + Calendar：2026-10-12 开始、提前三个自然日，得到 2026-10-09，并列出规定要求的材料。 |
| 英文通勤补助 | 先追问雇佣类型和每周现场办公天数。补充后给出基于用户自述的条件性判断，明确仍需雇主确认。 |
| 模拟工作日 | 2026-10-02 至 10-06 含首尾，在模拟周一至周五日历下为三个工作日；明确这未确认公司节假日。 |

最终四个流程均通过状态、预期工具和严格依据验证断言；它们是功能 smoke，不是大规模质量评估，也没有独立 Judge 或人工审核。源政策与问题见 [虚构测试集](../evals/agent-workflows.json)。

最终成功运行 24 个模型/Embedding 请求，报告 token 总量 32,927，包含索引与追问的估算费用 USD **0.01040254**。最终回答轮耗时约 7.94–16.82 秒，通勤场景另有前一轮追问耗时；这不是稳定的 P50/P95 benchmark。费用基于配置单价，不等于服务商账单。

首次真实运行暴露了“规划器过早交接，回答阶段因缺用户条件拒答”的问题，详见 [修复前结果](../reports/agent-stage2/live-smoke-before-clarification.json)。没有删除失败记录；增加回答阶段的结构化追问后重跑成功。两次有用量记录的运行费用合计 USD **0.01908548**。另外保留 [最初的临时目录权限失败](../reports/agent-stage2/live-smoke-first.json)，该次未记录任何 API 操作。

## 自动测试与限制

- 全项目测试数量与覆盖率见 [动态测试报告](../reports/tests.md)，Ruff lint/format 均通过。新测试覆盖权限撤销、跨用户任务、元数据/模型/索引变化、上下文伪造、过期/并发/容量限制、计算与日期边界，以及生成阶段追问恢复。
- 当前本机 PostgreSQL 测试仍因未配置测试数据库跳过，包括新增的 Agent SQLite/pgvector 共用检索权限合同中的 pgvector 分支；不把跳过算通过。既有远程 CI/Docker 记录属于旧版本，本阶段尚未重新运行远程验收。
- 多轮状态存于单进程内存，应用重启会失效；未提供跨进程/多副本状态共享。同步请求只有 Provider 超时和次数限制，取消接口不能中断在途 HTTP 调用。
- 真实业务日历、HR 余额、审批状态、申请提交尚未接入。Mock 标记和用户自述限定不能替代真实系统验证；模型依据校验也不是形式化正确性证明。
- 未添加页面按钮或修改聊天界面，未安装 LangGraph、增加外部写入工具或人工审批流程。

复现：

```powershell
.\.venv\Scripts\python.exe -m scripts.check
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
# 显式允许付费调用，仅使用虚构 PDF 与问题
.\.venv\Scripts\python.exe -m scripts.agent_live_smoke --live
```

第三阶段接入页面：Agent 模式、多轮补充、分类来源卡片、工具执行记录与实际场景演示。当前阶段完成后等待用户确认。
