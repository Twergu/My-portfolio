# Knowbase · Enterprise Knowledge AI Assistant

PDF 上传 → 逐页解析 → 分块 → Embedding → 向量检索 → 结构化回答 → 原文与断言依据校验 → 物理页引用。中日双语界面、OpenAI 兼容 Provider、PostgreSQL + pgvector、评估数据集、分块实验和 Docker Compose。

查看 [全部源文件](SOURCE_INDEX.md)、[17 项修改说明](docs/change-report.md)、[架构与设计决定](docs/architecture.md)。

## 运行与测试状态

**测试数量不在 README 中写死。** 执行下面命令后，程序从本次 pytest JUnit XML 生成 [测试报告](reports/tests.md) 和 [JSON 数据](reports/tests.json)，记录通过、失败、错误、跳过数量、时间与源码摘要。报告是注明时间的运行快照，跳过不算通过。

~~~powershell
.\.venv\Scripts\python.exe -m scripts.check
~~~

[CI](.github/workflows/ci.yml) 使用真实 pgvector 服务运行存储契约测试，生成评估/数据库基准报告，并构建启动 Compose 验证健康检查。工作流已提供，未执行时不能当作验证通过。

本次实测见 [分块实验](reports/chunks/chunk-experiment-local.md)、[数据库基准](reports/store-benchmark.md)、[真实 API 状态](reports/live-api-smoke.md)。缺少服务凭据或数据库环境时明确显示 blocked，不使用模拟结果代替实测。

## 本机启动

需要 Python 3.11 或更新版本。原生 HTML/JavaScript/CSS 无需前端编译。

~~~powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe run.py
~~~

已有环境可运行 start.ps1。在同一台电脑打开 [应用](http://127.0.0.1:8000/)，保持终端运行；端口被占用可使用 run.py --port 8001。127.0.0.1 是本机地址。macOS/Linux 使用 .venv/bin/python 对应执行。锁文件包含运行与测试依赖。

默认 SQLite + 本地原文检索，无需 API，按词项哈希向量直接返回原文，不生成 AI 答案。配置 RAG_DATABASE_URL 后启用 PostgreSQL；在 AI 问答模式下启用真实 Embedding 和 LLM。

## 使用与日文支持

1. 在「文档知识库」上传 PDF，或导入示例员工手册。支持多选、拖拽、去重、重试和删除。
2. 就绪后，在「知识问答」选择资料范围并提问。点击引用查看摘录和 PDF 实际页。
3. 顶栏或模型设置可切换「日本語」，选择保存在当前浏览器。日文界面发送 language: "ja"，全汉字问题也要求日语回答；API 接受 zh、ja、en。

支持有文字层的日文 PDF 与汉字、平假名、片假名检索。AI 日语质量取决于配置模型。扫描件仍需 OCR，多栏和表格质量取决于源文档。问答每次独立检索，刷新页面不保留对话。

## 模型 API 与真实验证

复制 [.env.example](.env.example) 为 .env，或在网页模型设置中配置服务：

~~~dotenv
RAG_MODE=api
RAG_BASE_URL=https://api.openai.com/v1
RAG_API_KEY=填写自己的服务密钥
RAG_CHAT_MODEL=填写服务支持的回答模型名称
RAG_EMBEDDING_MODEL=填写服务支持的向量模型名称
~~~

回答与 Embedding 使用同一服务地址和密钥。Base URL 为 API 根路径，不包含 /embeddings 或 /chat/completions 后缀。远程使用 HTTPS，本机服务可使用 HTTP。网页密钥仅保留在服务内存，不返回浏览器或写入数据库；.env 密钥由用户本地保存。变更服务地址不会把旧密钥带到新服务。网页保存的非密钥配置优先于环境默认值。

普通「测试连接」验证一次 Embedding 与一次回答接口。完整真实流程运行：

~~~powershell
.\.venv\Scripts\python.exe -m scripts.live_smoke --output reports/live-api-smoke
~~~

它生成两页虚构 PDF，在独立临时库中上传、解析、调用真实 Embedding、检索、生成 JSON 断言、再次调用 LLM 校验，检查金额与第 2 页引用。无密钥时不请求服务，写入 blocked 报告。通过只代表这一次端到端检查成功，不代表整体模型质量合格。

兼容服务需支持 JSON object 回答。正常 RAG 问答包括问题 Embedding、生成和依据校验，均按服务方规则计费；资料文本会发给用户配置的服务。真实全量评估和分块实验仅在显式 --mode api 时调用 API。

## 结构化拒答和依据校验

模型返回 status 与 claims。每条 claim 含 text 和 evidence[{source_id, quote}]，不允许额外自由文本答案。服务器先核对摘录是否存在于指定来源，再用一次独立校验调用检查原文是否支持每条断言，包括数字、条件、范围与否定。

缺引用、伪造摘录、矛盾断言、校验漏项或格式错误都不能直接展示。业务根据 answered、retrieval_only、insufficient_evidence、unsupported_answer、invalid_model_response 判断，不依赖特殊拒答字符串。响应保留 refused 兼容字段，并附 claims、support、完整 retrieved_sources 和 metrics。文件名、物理页码和原文由服务器映射。

自动依据校验仍可能误判，不是“零幻觉”或形式化证明。真实质量验收需要独立数据和人工检查。

## 评估、Latency 与 Cost

[评估协议](evals/README.md) 和 [数据集](evals/dataset.json) 包含中日英问题、页级 ground truth、参考事实与答案、无答案及提示注入案例，明确 dev/test 划分与局限。

~~~powershell
.\.venv\Scripts\python.exe -m scripts.evaluate --mode local --split test --output reports/evaluation-local-test
.\.venv\Scripts\python.exe -m scripts.chunk_experiment --mode local --output-dir reports/chunks
# 已配置模型服务后，执行真实 API 评估：
.\.venv\Scripts\python.exe -m scripts.evaluate --mode api --split test --output reports/evaluation-api-test
~~~

- Retrieval：页级 Recall@K、Precision@K、MRR@K、nDCG@K，以及无答案问题误检率。重复页去重，缺少位置不缩小 precision 分母。
- 回答质量：参考事实覆盖、token F1、规范化 exact match、正确拒答、答案失败/误拒答、候选断言 groundedness。词项指标与模型校验均标明局限；本地检索的生成质量为 N/A。
- Latency：解析、分块、索引 Embedding、写库、问题 Embedding、检索、生成、校验及总耗时；聚合平均值、p50/p95 和样本数。嵌套阶段不能直接相加。
- Cost：真实响应的 token usage、请求/重试次数，按配置单价估算，缺用量或单价时为未知。包括失败请求和校验请求。

在 .env 设置每百万 token 美元单价；留空表示未知，更换服务/模型时同步更新：

~~~dotenv
RAG_EMBEDDING_USD_PER_MILLION_TOKENS=
RAG_CHAT_INPUT_USD_PER_MILLION_TOKENS=
RAG_CHAT_OUTPUT_USD_PER_MILLION_TOKENS=
~~~

回答下方可展开「性能与用量」。GET /api/metrics 返回本进程最近的操作；测量随轮转日志保存在 data/logs/service.log。日志记录真实异常栈、文档 ID、阶段与索引身份，并保留 PDF 子进程失败栈。

## Chunk 实验与物理页边界

大小以字符计，默认 size=900、overlap=120，可在网页修改，overlap 必须小于 size。参数进入索引身份，修改后需重建；旧索引不混入新配置检索。

实验比较 (450,0)、(450,60)、(900,0)、(900,120)、(1200,120)、(1200,180)。仅用 dev 选择参数，再测试冻结配置；不根据 test 分数反复选择，也不以小型本地实验自动修改生产默认值。

**每个 Chunk 仍不跨物理页**，理由、代价与扩展方向见 [ADR 0001](docs/adr/0001-physical-page-chunks.md)。跨页问题可检索多页，为同一断言附多个来源。

## PostgreSQL + pgvector 与迁移

设置 RAG_DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE 后，配置、文档、Chunk 和原生 vector 使用 PostgreSQL，数据库连接池复用。PDF 原件保存在 RAG_DATA_DIR/files/。SQLite 保留为离线开发与比较基线。

默认 exact cosine；RAG_SEARCH_MODE=hnsw 或网页选择 HNSW 可用近似检索。目前 HNSW 使用 vector 类型，支持最多 2,000 维，需 PostgreSQL 与 API 模式。本地 2,048 维向量使用 exact；不静默截断或降精度。模型/profile/维度隔离。

已有 SQLite 不会自动迁移。先停止应用，备份数据库与 PDF，在目标库和文件目录为空时执行：

~~~powershell
.\.venv\Scripts\python.exe -m scripts.migrate_sqlite --source data --target-data-dir pgdata
# 上一条只校验；配置 RAG_DATABASE_URL 后显式执行：
.\.venv\Scripts\python.exe -m scripts.migrate_sqlite --source data --target-data-dir pgdata --apply
~~~

校验 SQLite 完整性、PDF 大小/SHA-256、Chunk 计数/维度/页码。源数据只读，目标事务失败回滚。成功后 RAG_DATA_DIR 指向目标目录。Docker 迁移需把相应文件目录挂载为应用数据卷；数据库和 PDF 必须来自同一次迁移。

数据库基准使用同 seed、向量和查询，排除模型耗时；记录预热后 p50/p95、索引耗时及相对独立 exact 参考的 Recall：

~~~powershell
# RAG_BENCHMARK_DATABASE_URL 指向可创建隔离 schema 的 pgvector 数据库
.\.venv\Scripts\python.exe -m scripts.benchmark_stores --count 1000 --dimensions 384 --queries 20 --repeats 3
~~~

仅创建并清理本次随机 schema。不配置数据库时仍测 SQLite，PostgreSQL 明确 blocked。未测两侧不声称性能提升。实际模型维度、更大规模和并发需要另外测量。

## Docker

需要可用的 Docker Engine/Compose。按 .env.example 配置 POSTGRES_PASSWORD 和 RAG_DATABASE_URL_DOCKER；后者的数据库主机为 db，密码中的特殊字符需 URL 编码。

~~~powershell
docker compose up --build -d --wait
docker compose logs -f app
~~~

打开 [应用](http://127.0.0.1:8000/)。Compose 提供 app 和 pgvector 数据库、健康检查、独立持久卷、非 root 应用用户和单索引进程。宿主机只在回环地址发布应用端口，数据库不直接开放到宿主机。

在运行的 Compose 中执行数据库基准并取回报告：

~~~powershell
docker compose exec app python -m scripts.benchmark_stores --database-url-env RAG_DATABASE_URL
docker compose cp app:/app/reports/store-benchmark.json reports/store-benchmark.json
docker compose cp app:/app/reports/store-benchmark.md reports/store-benchmark.md
~~~

使用 docker compose down 停止，命名数据卷保留。当前仍是单用户原型；组织权限、审计、分布式任务调度和对外服务的 TLS 尚未完成。

## 当前边界

单 PDF 上限 20 MB、200 页、100 万字符、2,000 个 Chunk；全库最多 100 份。单 worker 索引，PDF 在子进程解析，超时 45 秒终止。不含 OCR、对话记忆、组织权限或生产级质量保证。OneDrive 等同步目录中的文件也可能被该软件同步。

接口文档：[OpenAPI](http://127.0.0.1:8000/docs)。实现细节和官方 API 参考见 [Architecture](docs/architecture.md)。
