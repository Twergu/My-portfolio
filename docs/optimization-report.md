# 第二轮优化：逐项修改方向与验收

> 本文件是上一轮的历史记录；新增 ACL、Hybrid 和 Reranker 的当前状态见 [本轮 12 项修改](retrieval-optimization-report.md)。

本轮使用 `policy-challenge-v2.1`。用户于 2026-09-15 补充额度后恢复真实 API 验证；模型答案、验证和成本均从实际调用记录中计算。代码发布到独立 `codex/rag-quality-v2` 分支；真实 CI 状态与版本以 [Actions](https://github.com/Twergu/My-portfolio/actions/workflows/ci.yml?query=branch%3Acodex%2Frag-quality-v2) 和 [README 实验汇总](../README.md) 为准，未完成的实验不计为通过。

| # | 要求 / 修改方向 | 实现与效果 | 验收范围 |
|---|---|---|---|
| 1 | 真实 Embedding + LLM | 两页 PDF 的真实端到端 smoke；识别余额不足且不再盲目重试 | 补充额度后已实际通过解析、Embedding、结构化生成、quote/claim 校验和第 2 页引用，见[报告](../reports/live-api-smoke.md) |
| 2 | 困难 Evaluation Dataset | 新增 48 文档、96 页、108 题；中日英、旧/新/草案、相似制度、数字陷阱、否定、例外、跨文档和无答案 | 结构与页级证据校验通过；同语言所有竞争版本在检索范围内；模板仍相关，尚非人工独立评测集 |
| 3 | 真实 RAG 质量评估 | Recall@1/3/5、MRR、nDCG；隔离输入的两个独立 Judge 请求评分 Correctness / Citation Groundedness；Refusal Accuracy | 正式真实模型结果见[冻结 test 报告](../reports/chunks-api/chunk-api-selected-test.md)，不以本地原文检索替代生成指标 |
| 4 | Chunk 参数由实验决定 | 六组真实 API 配置全部完成；只用 dev 选出 900/0 并冻结后运行 test | [API 对照](../reports/chunks-api/chunk-experiment-api.md)；900/1200 四组产生同样边界，不能归因参数改善。本机示例使用 900/0，通用默认值保持，待长页验证 |
| 5 | 校验器误拒答分析 | 分别记录 quote_mismatch、unsupported_answer、invalid_model_response、false_refusal；被拦截候选由独立 Judge 复核 | 真实候选记录见各评估 JSON；引用 Judge 看不到 gold evidence，防止借用未引用证据高估支持度；公开 HTTP 不返回被拦截候选 |
| 6 | Generator / Verifier 分离 | `chat_model`、`verifier_model` 独立；真实对比 Luna 与 gpt-4.1-mini Verifier，各跑完整 dev | [模型试验](../reports/api-results.md)：Mini 只多答对一题且答案独立生成，不足以证明改善，保留经济基线；修改不影响 Embedding profile |
| 7 | Verification 模式 | off：schema/来源编号；fast：再校验原文 quote；strict：再调用模型逐断言验证 | [三模式真实测试](../reports/verification/comparison.md)全部完成；strict 有误拦截且延迟/成本更高，off/fast 不宣称运行时语义验证通过 |
| 8 | PostgreSQL 验收 | GitHub Linux runner 使用真实 pgvector 服务；CI 必须有测试 URL，任何 skipped 都算失败 | 实际数据库结果从 Actions 下载保存，见 README；本机没有安装 PostgreSQL |
| 9 | 1k/10k/100k Exact vs HNSW | 同 seed、384 维、20 查询、3 次重复；独立 float64 NumPy 真值；预热排除；报告构建时间、大小、计划和召回 | 通过真实 GitHub PostgreSQL 运行；只有完成记录才计为 measured，不预设 ANN 一定更好 |
| 10 | HNSW 生命周期 | 创建移到写入事务和维护路径；重建/删除清理废弃 profile 索引；查询不做 DDL | 真实 PG 测试覆盖旧索引清理、缺索引明确报错、入库前准备和删除清理 |
| 11 | Docker 完整启动 | 首次启动自动生成数据库随机密码、持久 secret 卷；无需 `.env` 即可 `docker compose up` | CI 构建与健康检查、PDF 入库、真实 HTTP 引用和重启持久性；结果见运行报告 |
| 12 | GitHub Actions 全绿 | 独立分支触发真实工作流；普通/PG 测试、双库/规模基准、Docker | 以当前分支实际工作流结论为准，未完成不宣称绿色 |
| 13 | Latency / Cost | 请求角色、各模型单价、tokens、平均 cost/query、P50/P95；Judge 开销与应用 query 分离 | 数据库、本地与 API 数据由实际请求计时/usage 生成；缺用量保留未知，见 README 和各实验 JSON |
| 14 | README 首页成果 | 动态 CI badge、困难集/Chunk/Vector 表格与可点报告；脚本从 JSON 更新 | 不手写测试通过数量；带运行范围和缺失值 |
| 15 | 后续 ACL | 下一阶段设计 User / Role / Document Permission，在检索前产生服务器端可访问文档集合，并覆盖 PDF、片段和列表接口 | 按用户“后续再加入”的顺序保留下一阶段；本轮未实现，当前仍为单用户 |
| 16 | 再后续 Audit Log | 下一阶段记录已认证用户、查询、候选/实际引用文档、拒绝访问、时间与请求 ID；绑定 ACL | 尚未实现；现有性能日志不能称为用户访问审计 |
| 17 | Agent 最后 | 等真实 RAG 评估、pgvector、Docker/CI 与访问边界稳定，再引入工作流和工具 | 本轮未引入 LangGraph 或 Agent，保留可靠 RAG 基础 |

## 指标的解释

Recall 截取实际 Top-K Chunk 后按物理页去重；重复片段不能从预算之外补出新的相关页。困难集不标注词项别名覆盖，避免把命中一个数字称为正确答案。Answer Correctness 使用参考答案、问题范围和 gold evidence，由单独配置的 Judge 判断完整性与错误；Citation Groundedness 单独依据实际引用片段判断。两者是自动评估，仍需人工抽样。

`false_refusal` 表示有答案题未交付答案，包含生成拒答及校验拦截，不表示这些拦截都不合理。`grounding_rejected_correct_and_grounded` 才统计被拦截候选经独立 Judge 判断既正确又有依据的情况。未配置 Judge 或发生 Judge 错误时不得输出完整质量验收。

独立 Judge 的判断也不是金标准。[三例分歧复核](../reports/grounding-case-review.md)发现一个“不含税”附加断言未获原文支持，但 Judge 仍判正确；运行时拦截在该例是合理的。原测量不改动，明确区分自动分数、事后 Codex 分析和将来独立人工验收。

本地 Chunk 对比有部分配置产生相同边界，因为页长短于参数值。这是观测结果；扩大真实长页资料后仍需重做实验。不跨物理页的设计继续由 [ADR 0001](adr/0001-physical-page-chunks.md) 约束。

本轮真实 API 的完整汇总、相同分块边界组、Verifier 试验和避免重复计费的账本见 [实验报告](../reports/api-results.md)。测试集 strict 正确性、引用支持度、拒答准确率和逐题失败原因均公开；不能以已交付答案的引用高分掩盖未交付答案。独立 Judge 遇到一次格式错误，已只补评原答案，原始失败及费用保留；现在格式错误最多重试一次，未恢复时仍让实验失败。

日文浏览器验收还修复了异步保存提示、重建提示、动态导航标题和引用面板按钮的漏译，PDF 原文及文件名继续保留原语言。真实模型日语生成和中文 PDF 引用单独记录为浏览器 smoke，不混入冻结测试集。

## 测试和凭据隔离

pytest 在导入应用前清空真实 API key，并禁止真正的 HTTPTransport 联网；PostgreSQL 驱动仍可连接显式测试数据库。真实 API smoke 是单独的显式脚本。`.env`、用户数据、缓存、测试临时文件均不进入源码包或 Git 分支。发布同步还检查本地密钥未进入待发布文件。
