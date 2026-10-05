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

完成实现与实测，P95 目标尚未改善。基线平均每任务 Planner 4.726 秒、Generator 3.608 秒、Verifier 2.394 秒、Knowledge Search 0.221 秒。`backend/agent.py` 新增可选 `answer_after`：最后一次只读工具成功且提供非空文本/来源后可直接交给 Generator；省去只负责 `prepare_answer` 的模型往返。空结果、失败和重复调用均不能走捷径，保留全部成功前提，并由 AgentService 再次 ACL 检查与 Strict/all 验证。

新增编排与双数据库 HTTP 安全回归，本地相关测试通过（数据库用例在最终 CI 实际执行）。[第一轮对照](../reports/agent-hardening/latency-first-attempt.md)保存了未达到目标的优化：Planner 次数 2.67→2.00，P50 12.259→10.997 秒，但 P95 18.122→20.132 秒、Task Success 50.0%→45.8%。不将此报告当作最终成功。

确认其中一例 business_task 检索直接交接而未进行 Calculator，故在后端增加限制：业务知识检索必须再规划；只有直接知识问答，或已经有制度前提的最终 Calculator/Calendar 调用可以提前交接。新增防过早交接测试与中途权限撤销测试。收紧后的相关测试 83 passed、18 PostgreSQL skipped（最终 CI 实际执行）。

[同集真实对照](../reports/agent-hardening/latency-comparison.md)：Planner 2.67→2.29 次/任务，P50 12.259→10.682 秒（约 -12.9%），平均成本 USD 0.002236→0.002147（约 -4.0%），Task Success 50.0%→70.8%。P95 18.122→19.904 秒，仍没有改善，不能宣称整体延迟均下降。生成结果和服务延迟有随机性；不是相同答案的因果对照。报告同时给出两次都成功交付的同题子集，主表保留全部失败题。

## P2-5 Policy Claim 约束

完成。新增 `backend/agent_grounding.py`，接入 `backend/rag.py` 与 `backend/agent_service.py`。引用的文档必须是服务器检索得到的 document/retrieved、有文档/分块/物理页身份、状态/日期适用；默认当前政策，显式 as_of 允许有效历史政策。草案、未分类、未来或过期文件不能证明当前业务许可。未引用的文档不能借用。

采用保守确定性门槛而非靠模型给 Claim 自报类型：每个自由文本 claim 均要求有效文档；无文档时只有服务器按结构化数值/日期生成的固定中日英计算表述可通过，不能加上“因此可报销/获准”等文字。User Input 保留自述来源，不能单独证明制度。所有接受的候选仍执行 Strict/all，不移除 Verifier。语义相关性仍需 Verifier，不能仅凭“有文档”证明正确。

同时修复评估中确认的 Generator 提示问题：不再把“雇主确认”附加到所有制度上，只在引用政策规定时保留；一般假设问题不能伪称用户实际自述。未改变 Verifier 接受标准。

新增 `tests/test_agent_policy_grounding.py`：故意放行的受控 Verifier、计算/自述伪装政策、未引用文档、过期/草案、固定计算加尾句、伪造显示文本、物理页身份等反例。相关测试 92 passed、18 PostgreSQL skipped（最终 CI 实际执行）。历史日文 fixture 原文不改，新的回归补充服务器文档身份，验证原错误在模型验证之前已被拒绝。

## P3-6 State 边界

完成。检查并保留单进程内存、每用户/全局容量、绝对 TTL、忙任务互斥、异常释放。最小修复：过期取消与续接都返回 404；慢请求不能返回过期续接句柄；首次运行创建 state 时立即绑定 PendingTask，让首次搜索后的重新索引在下一次 Planner 调用前也能被检测，而不是等 runner 返回才发现。

`tests/test_agent_integration.py` 新增真正的并发线程测试（不是只改 busy 标志），同时回复/取消/他人访问只能有一次模型路径；测试不滑动续期、TTL 边界、慢澄清、异常释放、全局容量与重启丢失句柄但保留文档。相关测试 79 passed、24 PostgreSQL skipped（最终 CI 实际执行）。[运行边界](agent-runtime.md)明确一个 worker、900 秒期限、100/4 容量、无硬中断、断线仍可能计费、重启需新任务，无 Redis/队列扩展。

## 最终验收

最终真实 API 评估已完成 24/24；应用代码 `fcfb60f05030055b7c4a05386c4aa3af53762e5f` 的[完整 GitHub Actions](https://github.com/Twergu/My-portfolio/actions/runs/37249750795)全绿。下载并核对 JUnit 与运行产物：**314 passed、0 failed、0 errors、0 skipped**，其中 [34 个 pgvector 参数用例](../reports/agent-hardening/ci-final/postgres-tests.json)全部实际执行；前端 15/15、Ruff、Docker 构建/健康/PDF 引用/重启持久化及 1k/10k/100k Vector Benchmark 均通过。[版本与步骤](../reports/agent-hardening/ci-final/provenance.json)、[自动测试报告](../reports/agent-hardening/ci-final/tests.md)、[Docker 结果](../reports/agent-hardening/ci-final/container-persistence.json)随源码保留。最终归档仅更新文档、报告及 README 表格生成文案，应用行为与该验收提交一致。

完整的 `evaluation-final-complete-live.json` 记录 24/24：Task Success 66.7%，Planning/Tool Selection/Clarification 均 100%，但六个工具场景因 quote mismatch 拦截。排查确认**新固定计算表述只在 metadata、未进入 source.text**，模型复制合法服务器计算表述时却无法通过精确引语检查。这是集成缺陷，不应放宽 quote 检查。

后续最小修复将同一服务器计算表述附入工具 source.text，原始计算文本保留；新增中日英 × Calculator/Calendar 六个对应回归。相关测试 104 passed、24 PostgreSQL skipped（最终 CI 实际执行）。该失败运行原样保留，修复后完整实测输出到新的 `evaluation-final-quoted-live.json`。

该轮 `return-deadline-en` 的 Correctness Judge 返回 `answer_correct=false`，reason 却明确说答案正确；报告依然按 false 计分，不根据有利解释手工改分。这是自动 Judge 的已知局限，非确定性后端保证。

P1 提交 `e41b980` 的[完整 CI](https://github.com/Twergu/My-portfolio/actions/runs/37198130074)为 269 passed、0 failed、0 errors、0 skipped；[原始报告](../reports/agent-hardening/ci-p1/tests.json)保留。工具引语修复后的本地全量为 280 passed、34 PostgreSQL skipped；上述最终 CI 实际执行了全部数据库用例，本地 skip 没有冒充通过。

`evaluation-final-live.json` 因执行进程中断仅保存 15/24，不能当作最终全量成绩，也不与重跑结果合并美化分数。保留该文件和其中全部失败；中断点可能已发出的请求和未保存的索引用量未知，不能计为零。新的完整评估输出为 `evaluation-final-complete-live.json`。

中断报告还暴露自动评估局限：`purchase-limit-zh` 把 5000 JPY 的审批路线门槛说成每单绝对上限，运行时 Verifier 与 Correctness Judge 都未指出；Grounding Judge 对“购买前收据”另有异议。虚构原文的收据时点措辞本身也不理想。保留原文、候选及全部 verdict，不修改历史评分。固定来源/有效期校验不能替代自然语言语义判断，自动 groundedness 不是人工保证。

### 最终真实 API 结果与未达标项

[最终逐题 JSON](../reports/agent-hardening/evaluation-final-quoted-live.json) / [Markdown](../reports/agent-hardening/evaluation-final-quoted-live.md)使用同一冻结数据集、同一模型与检索配置，24 个场景全部执行，未筛掉失败。真实 API 运行使用隔离 SQLite；PostgreSQL 的全量回归由 CI 单独验证，不能把两者拼成真实 API + PostgreSQL 端到端实测。

| 指标 | 基线 | 最终版本 |
| --- | ---: | ---: |
| Task Success Rate | 12/24，50.0% | 19/24，79.2% |
| Planning Success | 21/24，87.5% | 23/24，95.8% |
| Tool Selection Accuracy | 22/24，91.7% | 23/24，95.8% |
| Clarification Accuracy | 23/24，95.8% | 24/24，100% |
| Answer Correctness / 全部可回答任务 | 7/18，38.9% | 13/18，72.2% |
| Grounded Answer Rate / 全部可回答任务 | 7/18，38.9% | 13/18，72.2% |
| 已交付回答中通过独立 Grounding Judge | 7/7 | 13/13 |
| Planner calls/task | 2.67 | 2.54 |
| Tool calls/task | 1.25 | 1.33 |
| 重复工具请求（被拦截） | 1 | 0 |
| P50 / P95 | 12.259 / 18.122 秒 | 13.232 / 20.328 秒 |
| 平均应用成本 | USD 0.002236/task | USD 0.002206/task |

六个不可执行任务均正确返回 unavailable。最终五个未成功任务：

- `commuter-clarify-ja`：Generator 再次追问雇佣身份及雇主确认，未调用 Verifier。固定回复只说全职，不明确排除 contractor；这是澄清充分性与数据集语义边界，不能记作 Verifier 误拒答。该测试协议只提供一次回复，所以仍计失败。
- `training-clarify-ja`：Planner 追问课程数量，固定回复未回答这一点，未执行 Calculator；工具/规划和最终任务均失败。
- `purchase-multiply-en`、`leave-mock-window-zh`、`return-purchase-cross-en`：模型自由改写了仅引用工具/用户输入的计算断言，被确定性 `applicable_document_required` 门槛拦截。计算文字本身没有据此授予业务权限，反映当前保守校验对有效计算释义的误拦截代价；不能归咎于 Strict Verifier，因为该步骤尚未执行。保留原候选，不放宽门槛美化成绩。

本轮没有 quote mismatch。此前六例的工具来源正文缺失缺陷已修复，但上述三例说明模型仍可能不遵守固定计算文本合同。下一步若改善，应设计可验证的结构化计算 Claim 渲染与对应安全回归，不能简单接受模型自报“非政策”标签。

最终模型耗时仍是瓶颈：Planner / Generator / Verifier 平均每任务分别 5.577 / 4.853 / 1.885 秒，Knowledge Search 0.193 秒。交接优化单独实验曾降低 P50 和成本，但最终加固版本相较基线 **P50、P95 均未下降**，成本仅约低 1.3%。[最终性能对照](../reports/agent-hardening/latency-final-comparison.md)保留所有题与成功同题子集；不得以较好的中间轮代替最终性能。

成本为配置单价估算，不含索引与独立 Judge，也不是账单对账。数据是 AI 制作、未人工审核的八项政策（同一个 PDF 的八页），覆盖跨政策/跨页推理，没有覆盖多 PDF 聚合。Clarification Accuracy 只检查是否按合同发生追问，不评估追问是否充分、冗余或措辞正确，因此 100% 不代表澄清质量完美。自动 Judge 曾出现漏判及自相矛盾，其高分不是人工验收；完整历史失败与中断数据均保留。

## 修改文件索引

| 文件 | 修改内容 |
| --- | --- |
| `backend/verification.py` | 日文规范性要求与已执行事实区分；同 claim 完整前提；不凭空附加雇主确认 |
| `backend/rag.py` | Agent 生成规则、严格验证前的确定性 Policy Evidence 门槛 |
| `backend/agent.py` | 最终工具受限交接；在首轮开始时交付服务器状态引用 |
| `backend/agent_service.py` | 固定计算表述、历史日期传递、过期取消/无效句柄修复、首轮证据变更检测 |
| `backend/agent_grounding.py` | 文档身份/状态/日期检查，服务器生成的中日英计算文本；无需模型分类标签 |
| `evals/agent-ja-regression.json` | 原真实失败的 Generator/Evidence/Verdict 冻结数据 |
| `evals/make_agent.py`, `evals/agent_dataset.json` | 24 场景可重建数据集与参考合同 |
| `evals/agent_metrics.py`, `evals/judge.py` | 规划与回答独立评分，明确分母、调用/阶段/成本，独立 Judge |
| `scripts/agent_diagnose.py`, `scripts/agent_verifier_replay.py` | 虚构政策上的真实多轮诊断和正反例 Verifier 回放 |
| `scripts/agent_evaluate.py`, `scripts/agent_compare.py` | 真实完整评估、逐题保存、失败保留、同集性能对照 |
| `scripts/agent_results_summary.py` | 由完整实测 JSON 自动更新 README Agent 表格 |
| `tests/test_agent_japanese_regression.py` | 日文原失败、条件/规范/已提交等回归 |
| `tests/test_agent_policy_grounding.py` | 不可信自述/工具冒充政策、无效文档、固定计算表述防绕过 |
| `tests/test_agent.py`, `tests/test_agent_integration.py` | 交接安全、双数据库 Agent/ACL、并发/过期/重启/重建索引 |
| `tests/test_agent_evaluation.py` | 数据集和指标合同、保留失败、禁止不完整/不同数据集性能对照 |
| `scripts/container_smoke.py` | Docker Agent API/前端门禁及既有 PDF/重启检查 |
| `README.md`, `SOURCE_INDEX.md` | 最新成果/限制入口、相对路径完整源码索引 |
| `docs/agent-evaluation.md`, `docs/agent-runtime.md`, 本文件 | 实验协议、运行边界与逐项 Modification Report |
| `reports/agent-hardening/*` | 原始失败、完整真实调用、性能和 CI 报告；模型/受控测试明确分开 |
