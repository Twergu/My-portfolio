# 本次 17 项修改：方向、内容与验证结果

代码、文档和可复现实验已整合。真实 API、真实 pgvector 对比和 Docker 启动分别记录验证状态；未具备运行条件的项不计为实测完成。测试数量直接查看 [本次自动生成报告](../reports/tests.md)。

| # | 要求与修改方向 | 已修改内容 | 效果与当前验证范围 |
| --- | --- | --- | --- |
| 1 | README 测试数量动态化 | [check.py](../scripts/check.py) 执行 pytest，从本次 JUnit XML 生成 Markdown/JSON；记录时间、源码 SHA 与通过/失败/跳过 | README 不再手写数量；报告随检查命令更新，过期快照与跳过项可识别 |
| 2 | SOURCE_INDEX 相对路径 | [source_index.py](../scripts/source_index.py) 根据当前文件自动生成 [目录](../SOURCE_INDEX.md) | 所有源码链接相对根目录，克隆或解压后仍可用；可生成校验过的完整源码包 |
| 3 | 真正记录索引异常 | [main.py](../backend/main.py) 使用 exception/exc_info，附 document_id/profile/stage；[parse_pdf.py](../backend/parse_pdf.py) 保留子进程原始 traceback | 日志可定位实际异常与失败阶段；测试验证 RuntimeError 和真实损坏 PDF 的解析栈；日志轮转保存 |
| 4 | 真实 Embedding + LLM | [live_smoke.py](../scripts/live_smoke.py) 生成两页虚构 PDF，走上传、解析、真实 Embedding、LLM、依据校验与第 2 页引用 | **尚未完成真实调用：缺 RAG_API_KEY。** [报告](../reports/live-api-smoke.md) 明确 blocked，没有把模拟服务算作真实成功 |
| 5 | RAG Evaluation Dataset | [dataset.json](../evals/dataset.json) 中日英三份虚构手册、15 页、36 题，含 reference facts、reference answer、页级证据、dev/test | 可复现的入门数据集，涵盖直接、跨页、无答案、攻击问题；仍需真实资料和人工扩充 |
| 6 | Retrieval 指标 | [metrics.py](../evals/metrics.py) 实现页级 Recall@K、Precision@K、MRR@K、nDCG@K、无答案误检率 | 重复页去重；缺额保留在 precision 分母；无答案题单列，不人为抬高召回成绩 |
| 7 | 回答质量指标 | 参考事实词项覆盖、token F1、exact match、正确拒答、答案失败/误拒答、候选 claim groundedness | 本地原文模式为 N/A；词项重合和模型校验明确不等于人工语义正确性，真实模型分数待 API 配置 |
| 8 | Latency 与 Cost | [telemetry.py](../backend/telemetry.py) 和 /api/metrics 记录阶段延时、实际 token usage、重试、费用估算；界面可展开明细 | p50/p95 与样本数可查；含失败和校验调用；缺单价或用量为未知，纯本地无调用成本为 0 |
| 9 | Chunk Size / Overlap 实验 | [chunk_experiment.py](../scripts/chunk_experiment.py) 实跑六组参数，只用 dev 选参，再评估冻结配置的 test | [实测报告](../reports/chunks/chunk-experiment-local.md)：dev Recall 相同；按预定规则选择 1200/120；test Recall=1.000、nDCG≈0.855。样本小且为本地哈希检索，没有据此改生产默认值 |
| 10 | 保留不跨物理页并写 ADR | [ADR 0001](adr/0001-physical-page-chunks.md) 写出物理页定位、可核对性、评估标签稳定性、跨页语义代价 | Chunk 内不跨页；跨页问题通过检索多个来源与多引用支持；设计已有回归检查 |
| 11 | HTTP Client 连接复用 | 应用生命周期持有一个 Provider/Client；索引、提问、校验和连接测试共享连接池，关闭应用时释放 | 连接与重试契约通过 MockTransport 测试；具备复用条件，**真实 indexing latency 改善幅度尚未测得** |
| 12 | Provider API 独立 | [providers.py](../backend/providers.py) 集中 transport、鉴权、重试、Embedding 响应校验、chat/JSON 解析；可注入 Client 或同接口对象 | RAG 不再包含 HTTP 请求实现；便于替换模型服务、测试失败路径及复用连接 |
| 13 | 不依赖 NO_EVIDENCE 字符串 | 使用严格 JSON status/claims 和服务器状态码字段判断 | 文档中即便含旧字面标记也不触发拒答；不足、格式错误、依据不足分别返回状态，保留 refused 兼容前端 |
| 14 | Citation 升级为断言有依据 | 严格 schema → 原文 quote 校验 → 按 claim 指定来源进行独立 LLM 依据校验；只渲染通过的 claims | 合法编号但假摘录、矛盾断言、校验漏项/重复/类型错误均有阻断测试。仍是模型校验而非数学证明，需要人工验收 |
| 15 | SQLite → PostgreSQL + pgvector | [postgres_store.py](../backend/postgres_store.py) 原生 vector、连接池、事务、profile/维度隔离、exact/HNSW；[迁移脚本](../scripts/migrate_sqlite.py) 显式迁空目标 | 应用全链路通过 Store 接口选择 PostgreSQL；SQLite 保留基线。**本机无 PostgreSQL，PG 集成测试跳过；现有用户数据未自动迁移** |
| 16 | SQLite vs pgvector Benchmark | [benchmark_stores.py](../scripts/benchmark_stores.py) 同 seed/向量/query、独立 exact 真值、预热、p50/p95、HNSW 建索引时间与召回 | SQLite 已实测；[报告](../reports/store-benchmark.md) 的 PG 两项为 blocked。**尚未完成双库对比，不能声称 pgvector 更快**；配置数据库后可一键补跑 |
| 17 | Dockerize | [Dockerfile](../Dockerfile)、[compose.yaml](../compose.yaml)、[.dockerignore](../.dockerignore)、[CI](../.github/workflows/ci.yml) | app+pgvector、非 root、健康检查、持久卷、回环端口、单进程；YAML 已解析验证。**缺 Docker Engine，镜像构建与容器运行仍未实测** |

## 已实测结果应怎样解释

六组 Chunk 实验均使用相同虚构数据，K=5，候选数量从 17 到 32。页级 Recall 达到 1 并不代表每个事实都正确召回或生成正确；本地模式只展示原文，回答质量为 N/A。选择结果是该种子集上的规则输出，不是生产最优参数。

SQLite 基准使用 1,000 条 384 维合成归一化向量、20 个问题向量、每题 3 次测量和额外预热；实际查询 p50/p95 与索引耗时见报告。它衡量存储/检索，不包含模型调用，也不代表真实企业文档相关性。

浏览器已验证中文/日文设置中的 size、overlap、检索方式，以及本地回答的引用页码、阶段延时和零 API 用量；同时修复了切换语言后侧栏残留旧语言的问题。原有演示 PDF 已用新的分块版本在本地重建，页面可继续使用。

## 完成剩余实测需要的条件

1. 在本地 .env 配置模型地址、两个模型名称及 RAG_API_KEY；运行真实 smoke。若需要费用数字，再填相应 token 单价。不要在聊天里粘贴密钥。
2. 提供可用的 PostgreSQL + pgvector，设置 RAG_TEST_DATABASE_URL 与 RAG_BENCHMARK_DATABASE_URL，运行测试和带 --require-postgres 的基准。
3. 使用可用的 Docker Engine/Compose，配置示例环境变量后执行 docker compose up --build -d --wait。CI 也包含对应运行步骤。

这些条件不足不影响源码和本地评估的交付，但第 4 项、完整第 16 项以及第 15/17 项的运行验收仍待完成。实际命令与配置格式见 [README](../README.md)。
