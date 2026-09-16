# Knowbase · Enterprise Knowledge AI Assistant

PDF 上传 → 逐页解析 → Embedding → 权限与版本范围 → Hybrid Retrieval → 可选 Reranker → 结构化回答 → 断言依据校验 → 物理页引用。中日双语界面、共享 OpenAI 兼容 Provider、PostgreSQL + pgvector、真实评估和 Docker Compose。

查看 [全部源文件](SOURCE_INDEX.md)、[本轮 12 项检索与权限优化](docs/retrieval-optimization-report.md)、[上轮 17 项优化记录](docs/optimization-report.md)、[首轮修改记录](docs/change-report.md)、[架构与设计决定](docs/architecture.md)。

[![CI](https://github.com/Twergu/My-portfolio/actions/workflows/ci.yml/badge.svg?branch=codex%2Frag-quality-v2)](https://github.com/Twergu/My-portfolio/actions/workflows/ci.yml?query=branch%3Acodex%2Frag-quality-v2)


## 本轮 v3 实测与配置

<!-- V3_RESULTS_START -->
真实三路检索 test：Dense / Hybrid / Hybrid+Reranker 的 Recall@5 分别为 88.1% / 88.1% / 100%；重排同时增加真实 API 延时和成本。完整质量和 CI 验收以 [逐项报告](docs/retrieval-optimization-report.md) 与 `reports/v3/` 的状态为准。
<!-- V3_RESULTS_END -->

在模型设置中选择 `retrieval_mode=hybrid`、`candidate_k=20`、`reranker_mode=llm` 即启用重排；可指定独立 `reranker_model`。当前默认 Dense/不重排保留便宜路径；Exact 仍是数据库默认模式。`strict + all` 检查全部断言，`selective` 跳过项始终标为未验证。

文档信息面板可编辑政策状态、版本、部门和生效区间；问答输入框上方可设置检索筛选。多人访问须先按 [ACL 配置步骤](docs/access-control.md) 启用 `RAG_AUTH_MODE=required`，不能把 local 开发模式当成身份认证。

## 上轮基线实验结果

本轮增加 Hybrid、Reranker、Verifier 校准、文档版本过滤及检索前 ACL，详见 [逐项修改与结果](docs/retrieval-optimization-report.md)。以下旧表为上一轮基线；新的对比见顶部 v3 结果。人工审核、Agent 与人在回路按要求暂缓。

<!-- EXPERIMENT_RESULTS_START -->
| 项目 | 实测结果与范围 |
|---|---|
| 本地测试 | passed，具体数量和时间见[动态报告](reports/tests.md) |
| CI / PostgreSQL 测试 | success；[验收运行](https://github.com/Twergu/My-portfolio/actions/runs/34936340277)，版本 `dd44061`；[数据库测试报告](reports/ci/tests.md) |
| 困难集 / 本地检索 | policy-challenge-v2.1；test Recall@1/3/5 = 0.5873 / 0.7500 / 0.8611；MRR=0.8302，nDCG=0.7819 |
| Chunk 实验 | 六组配置；dev 选择 450/0，仅适用本地基线；[完整结果](reports/chunks-v2/chunk-experiment-local.md) |
| 1,000 chunks / exact | measured：P50/P95 = 3.2678/3.5175 ms；Recall@5=1.0000 |
| 1,000 chunks / hnsw | measured：P50/P95 = 3.9125/3.9688 ms；Recall@5=1.0000 |
| 10,000 chunks / exact | measured：P50/P95 = 11.0706/11.5921 ms；Recall@5=1.0000 |
| 10,000 chunks / hnsw | measured：P50/P95 = 4.7553/4.9425 ms；Recall@5=0.5500 |
| 100,000 chunks / exact | measured：P50/P95 = 102.2489/144.1431 ms；Recall@5=1.0000 |
| 100,000 chunks / hnsw | measured：P50/P95 = 8.2030/8.9119 ms；Recall@5=0.1400 |
| Vector Benchmark | [硬件、方法、构建耗时与索引大小](reports/vector-scale.md)；合成向量、单客户端、热缓存，不代表语义检索质量 |
| SQLite vs pgvector / 1k | P50 ms：sqlite_exact 169.2853 / pgvector_exact 3.2762 / pgvector_hnsw 3.9129；[对照报告](reports/store-benchmark.md) |
| Docker | passed：App + pgvector、PDF 索引与引用、应用重启持久性；[验收数据](reports/ci/container-persistence.json) |
| 真实 API 流程 | passed；PDF→Embedding→结构化回答→原文/断言校验→物理页引用；[真实 smoke](reports/live-api-smoke.md) |

以上数据来自 JSON 运行快照，使用 `python -m scripts.results_summary` 更新。测试数量始终引用自动报告；本地哈希检索分数不等于真实模型准确率。

| 真实 RAG 测试集 | 实测结果 |
|---|---|
| 版本 / 范围 | policy-challenge-v2.1；54 题；gpt-5.6-luna / verifier gpt-5.6-luna；[完整逐题结果](reports/chunks-api/chunk-api-selected-test.md) |
| Recall@1/3/5 | 0.5833 / 0.8452 / 0.8810 |
| MRR / nDCG | 0.8254 / 0.8055 |
| Correctness / Citation Groundedness / Refusal Accuracy | 0.8333 / 1.0000 / 0.8519 |
| Quote mismatch / Unsupported / False refusal | 0.0000 / 0.0556 / 0.1667 |
| Query P50 / P95 | 5426.1470 / 9751.6545 ms；2 workers；不含额外 Judge |
| 平均应用 cost/query | USD 0.00081014 |
| 实验与额外评估开销 | [分块对比](reports/chunks-api/chunk-experiment-api.md)；[验证模式](reports/verification/comparison.md)；Judge 不计入用户 query 成本 |

答案正确性与引用支持度分别调用独立 Judge，引用评分看不到 gold evidence。指标分母及限制见评估协议；单次合成集结果仍需真实资料与人工复核。
真实 API 开发集冻结 **900/0**。900/1200 的四组配置产生相同文本边界，单次得分差异不足以证明分块效应；[边界分析与费用账本](reports/api-results.md)。本机演示已使用冻结配置，代码的通用默认值仍需目标文档验证。

| 验证模式（同一 test） | Correctness | False refusal | P50 / P95 ms | 平均 USD/query |
|---|---:|---:|---:|---:|
| off | 0.9762 | 0.0238 | 3527.5054 / 6822.6271 | 0.00057060 |
| fast | 0.9286 | 0.0238 | 3389.1299 / 6984.6610 | 0.00056931 |
| strict | 0.8333 | 0.1667 | 5426.1470 / 9751.6545 | 0.00081014 |
各模式独立生成一次，存在随机性，不能当作相同答案的因果对照。off/fast 在运行时没有语义依据保证；当前 strict 有误拦截，保留风险说明而不根据 test 成绩继续改提示词。
本轮有记录的实际调用估算总费用 **USD 2.084806**，含索引、额外 Judge、诊断基线和补评；不含税费，不能替代账单。
HNSW 表格使用 ef_search=100；完整报告另列 400/1000 的召回与延时。默认仍选 Exact，只有目标数据的召回和延时都达标才切换 HNSW。CI 的 Docker 验收来自全新 Linux runner，本机尚未安装 Docker。
<!-- EXPERIMENT_RESULTS_END -->

## 运行与测试状态

独立 Judge 也会误判。事后原文复核发现，它曾把资料未说明的“不含税”判为有依据；该答案已被运行时 Verifier 拦截。参见 [依据验证分歧与反例](reports/grounding-case-review.md)。自动 Citation Groundedness 和误拒答诊断不等同于人工验收。

**测试数量不在 README 中写死。** 执行下面命令后，程序从本次 pytest JUnit XML 生成 [测试报告](reports/tests.md) 和 [JSON 数据](reports/tests.json)，记录通过、失败、错误、跳过数量、时间与源码摘要。报告是注明时间的运行快照，跳过不算通过。

~~~powershell
.\.venv\Scripts\python.exe -m scripts.check
~~~

[CI](.github/workflows/ci.yml) 使用真实 pgvector 服务运行存储契约测试，生成评估/数据库基准报告，并构建启动 Compose 验证健康检查。工作流已提供，未执行时不能当作验证通过。

本次实测见 [分块实验](reports/chunks-v2/chunk-experiment-local.md)、[数据库基准](reports/store-benchmark.md)、[真实 API 状态](reports/live-api-smoke.md)。缺少服务凭据或数据库环境时明确显示 blocked，不使用模拟结果代替实测。

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
RAG_VERIFIER_MODEL=填写验证模型名称或留空复用回答模型
RAG_VERIFICATION_MODE=strict
RAG_EVAL_JUDGE_MODEL=填写独立评估模型名称
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

Generator 与 Verifier 可分别配置；同模型的两次调用仍可能犯相似错误。`off` 只检查 JSON 结构和来源编号，`fast` 增加原文摘录匹配，默认 `strict` 再做逐断言模型依据校验。off/fast 的响应明确标为语义依据未验证；结构化拒答不会伪装成正确答案。

模型返回 status 与 claims。每条 claim 含 text 和 evidence[{source_id, quote}]，不允许额外自由文本答案。strict 模式下服务器先核对摘录是否存在于指定来源，再用一次校验调用检查原文是否支持每条断言，包括数字、条件、范围、有效日期与否定。

缺引用、伪造摘录、矛盾断言、校验漏项或格式错误都不能直接展示。业务根据 answered、retrieval_only、insufficient_evidence、unsupported_answer、invalid_model_response 判断，不依赖特殊拒答字符串。响应保留 refused 兼容字段，并附 claims、support、完整 retrieved_sources 和 metrics。文件名、物理页码和原文由服务器映射。

自动依据校验仍可能误判，不是“零幻觉”或形式化证明。真实质量验收需要独立数据和人工检查。

## 评估、Latency 与 Cost

[评估协议](evals/README.md) 和 [数据集](evals/dataset.json) 包含中日英问题、页级 ground truth、参考事实与答案、无答案及提示注入案例，明确 dev/test 划分与局限。

默认实验使用 [困难集 policy-challenge-v2.1](evals/hard_dataset.json)：48 份文档、96 页、108 道题，dev/test 各 54 题，覆盖旧/新制度、草案、相似文档、数字陷阱、否定、例外、跨文档及无答案。两组公司与金额隔离，检索范围同时包含竞争版本；模板仍有相关性，需人工和真实资料继续扩充。

~~~powershell
.\.venv\Scripts\python.exe -m scripts.evaluate --mode local --split test --output reports/evaluation-local-test
.\.venv\Scripts\python.exe -m scripts.chunk_experiment --mode local --output-dir reports/chunks-v2
# 已配置模型服务后，执行真实 API 评估：
.\.venv\Scripts\python.exe -m scripts.evaluate --mode api --split test --output reports/evaluation-api-test
~~~

- Retrieval：Recall@1/3/5、MRR@K、nDCG@K、Precision@K 与无答案误检率。先截取实际 Chunk 预算，再按物理页去重。
- 回答质量：独立 Judge 基于 reference answer / gold evidence 评分 Answer Correctness 与 Citation Groundedness；另列 Refusal Accuracy、quote 匹配失败、unsupported answer、false refusal。被拒候选会单独接受 Judge 检查，用于发现正确且有依据的答案被验证器拦截；它们不进入公开回答。
- 运行时 Verifier 的通过率与独立 Judge 分数分开；词项 F1/覆盖只作为代理指标。本地检索没有生成答案，语义质量为 N/A。Judge 也可能出错，需要人工复核。
- Latency：解析、分块、索引 Embedding、写库、问题 Embedding、检索、生成、校验及总耗时；聚合平均值、p50/p95 和样本数。嵌套阶段不能直接相加。
- Cost：真实响应的 token usage、请求/重试次数，按配置单价估算，缺用量或单价时为未知。包括失败请求和校验请求。

在 .env 设置每百万 token 美元单价；留空表示未知，更换服务/模型时同步更新：

~~~dotenv
RAG_EMBEDDING_USD_PER_MILLION_TOKENS=
RAG_CHAT_INPUT_USD_PER_MILLION_TOKENS=
RAG_CHAT_OUTPUT_USD_PER_MILLION_TOKENS=
RAG_VERIFIER_INPUT_USD_PER_MILLION_TOKENS=
RAG_VERIFIER_OUTPUT_USD_PER_MILLION_TOKENS=
RAG_JUDGE_INPUT_USD_PER_MILLION_TOKENS=
RAG_JUDGE_OUTPUT_USD_PER_MILLION_TOKENS=
~~~

回答下方可展开「性能与用量」。GET /api/metrics 返回本进程最近的操作；测量随轮转日志保存在 data/logs/service.log。日志记录真实异常栈、文档 ID、阶段与索引身份，并保留 PDF 子进程失败栈。

实验报告把日常 query cost 与额外 Judge 成本分开，输出 token usage、平均 cost/query、P50/P95。不同模型使用对应单价；费用为标准价格估算，尚不计缓存折扣。三种验证模式的付费实验命令为 `python -m scripts.verification_experiment --run-api`。正式协议将正确性 Judge 与引用 Judge 的输入隔离，避免用未引用的参考证据补全引用支持度。

## Chunk 实验与物理页边界

大小以字符计，默认 size=900、overlap=120，可在网页修改，overlap 必须小于 size。参数进入索引身份，修改后需重建；旧索引不混入新配置检索。

实验比较 (450,0)、(450,60)、(900,0)、(900,120)、(1200,120)、(1200,180)。API 模式以 dev Answer Correctness 优先，再比较 Recall/nDCG/Chunk 数；local 模式只用检索成绩。评估 Chunk ID 固定，避免同分排序受随机 ID 影响。最后测试冻结配置，不根据 test 调参。[本地困难集结果](reports/chunks-v2/chunk-experiment-local.md) 只适用于本地基线，真实 API 参数待评估后决定。

**每个 Chunk 仍不跨物理页**，理由、代价与扩展方向见 [ADR 0001](docs/adr/0001-physical-page-chunks.md)。跨页问题可检索多页，为同一断言附多个来源。

## PostgreSQL + pgvector 与迁移

设置 RAG_DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE 后，配置、文档、Chunk 和原生 vector 使用 PostgreSQL，数据库连接池复用。PDF 原件保存在 RAG_DATA_DIR/files/。SQLite 保留为离线开发与比较基线。

默认 exact cosine；RAG_SEARCH_MODE=hnsw 或网页选择 HNSW 可用近似检索。目前 HNSW 使用 vector 类型，支持最多 2,000 维，需 PostgreSQL 与 API 模式。本地 2,048 维向量使用 exact；不静默截断或降精度。模型/profile/维度隔离。

HNSW 在索引写入事务、启动或设置维护时建立；用户查询不会 CREATE INDEX。最后一份文档重建到新 profile 或被删除后，废弃索引会清理。维护仅管理本应用保留命名空间下的索引，操作使用数据库 advisory lock 串行化。

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
.\.venv\Scripts\python.exe -m scripts.benchmark_scale --sizes 1000 10000 100000 --dimensions 384 --queries 20 --repeats 3
~~~

仅创建并清理本次随机 schema。不配置数据库时仍测 SQLite，PostgreSQL 明确 blocked。未测两侧不声称性能提升。实际模型维度、更大规模和并发需要另外测量。

## Docker

需要可用的 Docker Engine/Compose。全新克隆无需 `.env` 或 API 密钥，直接运行 `docker compose up` 即启动本地检索 App + PostgreSQL + pgvector。首次启动会生成随机数据库密码并保存在独立持久卷，重启复用；AI 模式再按 `.env.example` 配置。

~~~powershell
docker compose up --build -d --wait
docker compose logs -f app
~~~

打开 [应用](http://127.0.0.1:8000/)。Compose 提供 app 和 pgvector 数据库、健康检查、独立持久卷、非 root 应用用户和单索引进程。宿主机只在回环地址发布应用端口，数据库不直接开放到宿主机。

在运行的 Compose 中执行数据库基准并取回报告：

~~~powershell
docker compose exec app python -m scripts.benchmark_scale --database-url-env RAG_DATABASE_URL
docker compose cp app:/app/reports/vector-scale.json reports/vector-scale.json
docker compose cp app:/app/reports/vector-scale.md reports/vector-scale.md
~~~

使用 docker compose down 停止，命名数据卷保留。默认 `RAG_AUTH_MODE=local` 为单用户开发模式；设置 `required` 并签发用户令牌后启用 ACL，见 [用户与权限配置](docs/access-control.md)。SSO、用户审计、分布式任务和对外 TLS 尚未实现。

## 当前边界

单 PDF 上限 20 MB、200 页、100 万字符、2,000 个 Chunk；全库最多 100 份。单 worker 索引，PDF 在子进程解析，超时 45 秒终止。不含 OCR、对话记忆、SSO 或生产级质量保证。OneDrive 等同步目录中的文件也可能被该软件同步。

接口文档：[OpenAPI](http://127.0.0.1:8000/docs)。实现细节和官方 API 参考见 [Architecture](docs/architecture.md)。
