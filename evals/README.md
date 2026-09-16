# RAG Evaluation Dataset 与指标协议

默认使用 `hard_dataset.json`，由 `python -m evals.make_hard` 重建。`policy-challenge-v2.1` 包含 48 份虚构制度、96 个物理页、108 道中日英问题，dev/test 各 54 题。两组公司和金额分别用于 dev/test，检索范围同时保留两组公司、旧版、现行版、草案和合同工制度，不能预先过滤掉干扰文档。原 `dataset.json` 是保留用于回归测试的 36 题种子集。

每题包含问题、语言、类别、检索范围、`answerable`、页级 `relevance`、`reference_answer` 和 `reference_evidence`。覆盖新旧版本、相似制度、数字陷阱、否定、例外、跨文档、无答案和提示注入。困难集不使用数字别名匹配充当答案正确性。v2.1 修正英文参考答案超出 gold 页的事实，并拆分审批规则，避免只读一份文件就回答标为跨文档的问题。页文本从 PDF 解析后开始，PDF 上传和解析另由 smoke 验证。

## Retrieval 指标

先截取实际返回的 Top-K Chunk，再按首次出现去重 `(document_id, page)`。分别报告 Recall@1/3/5；MRR@K、nDCG@K 使用请求 K（默认 5）。重复页不会从预算之外补进新页。未填满位置仍计入 precision 分母。

| 指标 | 定义 |
| --- | --- |
| Recall@K | 命中的不同相关页数 / 全部相关页数 |
| Precision@K | 命中的不同相关页数 / K |
| MRR@K | 第一个相关页的排名倒数，未命中为 0 |
| nDCG@K | 以 `2^grade - 1` 为增益、`log2(rank+1)` 折扣，除以理想 DCG |
| 无答案问题误检率 | 无答案问题中至少返回一页的比例，独立展示 |

无答案问题的 Recall/Precision/MRR/nDCG 不适用，不能当成满分。汇总是可适用题目的宏平均，报告附样本数。页级召回不代表召回了整页每一条事实，因此答案与摘录仍需要另外校验。

## 回答质量

| 指标 | 解释与限制 |
| --- | --- |
| Answer Correctness | 单独配置的 Evaluation Judge 根据问题、参考答案和 gold evidence 检查答案正确性与完整性；有答案题未交付回答计 0 |
| Citation Groundedness | Judge 独立检查实际引用对每条断言的支持，另做摘录匹配；不继承运行时 Verifier 的通过标志 |
| Refusal Accuracy | 有答案题交付回答、无答案题结构化拒答的比例；只评价拒答决策，不评价回答内容 |
| quote_match_failure / unsupported_answer | 摘录匹配失败比例、依据检查拦截比例 |
| grounding_rejected_correct_and_grounded | 被拦截候选中，经 Judge 判定正确且有依据的比例；附候选样本数，用于发现误拦截 |
| Expected facts coverage | 参考事实的别名在回答中出现的比例，是词项代理指标；命中数字不代表语义正确 |
| Reference token F1 | 参考答案和生成答案之间的 token 重合 F1；中日文按字符、英文按词处理 |
| Reference exact match | 规范化 token 序列是否相同，不能正确评价所有改写 |
| Correct refusal | 无答案题是否以结构化 `insufficient_evidence` 拒答；格式错误和依据校验失败不算正确拒答 |
| False refusal | 有答案题是否未产出通过依据校验的答案（包括被拦截的候选答案） |
| Claim groundedness | 所有候选断言中通过依据检查的比例，包括被拦截答案的候选断言 |
| All claims grounded | 该题候选断言是否全部获支持 |

本地模式仅返回原文，因此回答质量为 N/A。运行时 `claim_groundedness` 是 Verifier 诊断值，off/fast 未做语义验证时为未知。独立 `citation_groundedness` 来自额外 Judge，仍不是人工标签。被拦截候选只供显式内部评估，不进入公开问答响应。未配置 Judge、调用失败或结果不完整不能标为完整质量验收。Judge 也会误判，上线前需人工抽样。

`false_refusal` 衡量可回答问题未交付答案的比例，不等于 Verifier 自身误判率：生成器产生无依据限定词而被正确拦截也计入该指标。v3 实际发现税额限定词被 Judge 漏判，以及 gold 页覆盖不足导致正确补充信息被 Judge 判错；原始分数保留，见 [分歧诊断](../reports/v3/grounding-diagnostics.md)。

## Latency 与 Cost

报告真实测量 indexing、query embedding、retrieval、generation、verification、provider HTTP、退避和整题耗时，聚合 p50/p95/平均值及样本数。不同阶段存在嵌套关系，不能直接把所有阶段相加。token usage 来自服务实际响应；成本按 `.env` 中配置的每百万 token 单价计算，包含回答与依据校验的两次 LLM 调用。

应用 query 成本与额外 Judge 成本分开，run cost 包含索引、问答和 Judge。没有调用 API 时成本为 0；缺少 usage、失败费用未知或缺单价时总成本为 null/N/A，保留已知部分。估算不含缓存折扣、税费或服务等级差异，不能代替账单。

## 运行

```powershell
.\.venv\Scripts\python.exe -m scripts.evaluate --mode local --split test --output reports/evaluation-local-test
.\.venv\Scripts\python.exe -m scripts.chunk_experiment --mode local --output-dir reports/chunks-v2
```

真实评估需配置密钥、服务、Generator/Verifier、`RAG_EVAL_JUDGE_MODEL` 和单价，再显式使用 `--mode api`。三种验证模式对比命令为 `python -m scripts.verification_experiment --run-api`。这些命令会调用付费接口；2026-09-15 补充额度后恢复执行。默认 local 不会调用；脚本使用隔离临时 SQLite 数据，不改应用知识库，存储性能另由 pgvector benchmark 评估。

正式协议 `isolated-correctness-and-citations-v2` 分别调用两个 Judge 请求：正确性看到参考答案和 gold evidence；引用支持度只看到问题和实际引用，不能借用未引用的参考证据。运行时 Verifier 标志也不进入 Judge 输入。旧单次 Judge 报告仅留作诊断与已发生费用记录，不参与正式选参。

`--concurrency 2` 使用两个问题 worker，各问题指标独立，报告标注并发数；应用延迟不含等待队列与额外 Judge 时间。Chunk/Verification 脚本支持 `--resume`，仅复用数据哈希、配置、Embedding profile、评分协议、Judge 与并发数完全匹配且已完成的报告；变化时要求另选输出目录。

Judge 的 JSON/schema 或断言编号不完整时最多追加一次格式重试；不会把缺失 verdict 当作通过。所有尝试保留实际 token/cost，`validation_failures` 记录环节与次数，不保存原始错误响应。正确性与引用评分的输入仍隔离，重试不提供期望分数。评估报告保存合成数据的 `evaluation_trace`，便于复核；这些实验文件可能包含数据集原文，使用企业资料评估时应按资料的访问要求保存。

本轮 `900/0 dev` 有一次 Judge 格式错误，已仅重评原来的一个答案，原回答和检索没有重新执行。此前失败快照保存在 `reports/judge-recovery/`，正式报告的 `judge_replays` 记录补评；正式费用已包含原失败调用，不能再把快照费用累加一次。

固定六组配置为 `(450,0)`、`(450,60)`、`(900,0)`、`(900,120)`、`(1200,120)`、`(1200,180)`，单位为字符且不跨物理页。API 按 dev Answer Correctness、Recall、nDCG、较少 Chunk 数依次选择，local 只用检索指标；冻结后才测 test，不按 test 调参。部分页短于配置值，900/1200 会产生相同边界，仍需真实长页进一步区分。规则模板和翻译有相关性，数据尚无独立人工验收，不能声称生产准确率或自动修改参数。

报告入口：[困难集分块实验](../reports/chunks-v2/chunk-experiment-local.md)、[冻结参数 test](../reports/chunks-v2/chunk-local-selected-test.md)、[真实 API 状态](../reports/live-api-smoke.md)。
