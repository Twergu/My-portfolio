# RAG Evaluation Dataset 与指标协议

`dataset.json` 是版本化的虚构企业制度种子集，不含企业真实资料。中、日、英三份文档共 15 个物理页，36 个问题：24 个 dev 问题用于参数选择，12 个 test 问题用于选择结束后的验证。数据由 `python -m evals.make_seed` 重建，修改标注时应同步更新生成器与 dataset_id。

每题包含 `id`、`language`、`split`、`category`、`question`、`document_ids`、`answerable`、页级 `relevance`（含 grade）、`expected_facts`（可接受表达别名）与 `reference_answer`。覆盖直接查询、跨页汇总、资料不足和提示注入。页文本代表 PDF 提取之后的边界；PDF 上传和真实解析由 `live_smoke.py` 另外验证。

## Retrieval 指标

从实际返回的 Top-K Chunk 中按首次出现顺序去重 `(document_id, page)`，使用页级证据排名。重复页不会增加得分。K 仍是原始请求的 Chunk 预算；缺少位置计入 precision 的分母，而不是缩小分母制造高分。

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
| Expected facts coverage | 参考事实的别名在回答中出现的比例，是词项代理指标；命中数字不代表语义正确 |
| Reference token F1 | 参考答案和生成答案之间的 token 重合 F1；中日文按字符、英文按词处理 |
| Reference exact match | 规范化 token 序列是否相同，不能正确评价所有改写 |
| Correct refusal | 无答案题是否以结构化 `insufficient_evidence` 拒答；格式错误和依据校验失败不算正确拒答 |
| False refusal | 有答案题是否未产出通过依据校验的答案（包括被拦截的候选答案） |
| Claim groundedness | 所有候选断言中通过依据检查的比例，包括被拦截答案的候选断言 |
| All claims grounded | 该题候选断言是否全部获支持 |

本地模式仅返回原文，因此回答质量指标为 N/A。Groundedness 使用模型依据校验结果，不是独立人工标签；该模型也可能误判，不能用这一指标证明答案必然正确。上线前需要人工核验语义正确性、完整性、相关性及引用的支持度，并在独立模型或人工复核集上验证自动校验器。

## Latency 与 Cost

报告真实测量 indexing、query embedding、retrieval、generation、verification、provider HTTP、退避和整题耗时，聚合 p50/p95/平均值及样本数。不同阶段存在嵌套关系，不能直接把所有阶段相加。token usage 来自服务实际响应；成本按 `.env` 中配置的每百万 token 单价计算，包含回答与依据校验的两次 LLM 调用。

没有调用 API 时成本为 0。服务缺少 usage、请求失败的费用未知、或未配置价格时，总成本为 null/N/A，同时报告已知部分。估算不含缓存折扣、税费或服务等级差异；单价应与当前服务和模型对应。

## 运行

```powershell
.\.venv\Scripts\python.exe -m scripts.evaluate --mode local --split test --output reports/evaluation-local-test
.\.venv\Scripts\python.exe -m scripts.chunk_experiment --mode local --output-dir reports/chunks
.\.venv\Scripts\python.exe -m scripts.live_smoke --output reports/live-api-smoke
```

真实评估需配置 `RAG_API_KEY`、模型名称及服务地址，再显式运行 `--mode api`。该模式会调用付费接口；默认 local 不会调用。所有脚本使用隔离的临时数据，不改应用已有知识库。

Chunk 实验比较六种预先固定的参数组合，以 dev Recall、dev nDCG、较少 Chunk 数依次选择；最后只测一次选定配置的 test 集。相同题材和翻译之间存在相关性，这只是入门评估集，不能将其结果当作真实企业文档准确率或自动修改生产参数。

报告入口：[分块实验](../reports/chunks/chunk-experiment-local.md)、[选定参数 test 验证](../reports/chunks/chunk-local-selected-test.md)、[真实 API 状态](../reports/live-api-smoke.md)。
