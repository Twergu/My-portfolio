# 真实 API 实验结果与费用

模型：text-embedding-3-small → gpt-5.6-luna → gpt-5.6-luna；独立评估 Judge：gpt-4.1。

数据集：policy-challenge-v2.1；六组 dev 配置后冻结 900/0，只对选中配置运行 test。

| 测试集指标 | 得分 | 样本数 |
|---|---:|---:|
| answer_correctness | 83.33% | 42 |
| citation_groundedness | 100.00% | 36 |
| refusal_accuracy | 85.19% | 54 |
| quote_match_failure | 0.00% | 54 |
| unsupported_answer | 5.56% | 54 |
| false_refusal | 16.67% | 42 |
| grounding_rejected_correct_and_grounded | 100.00% | 3 |

Citation Groundedness 只统计交付答案的逐题平均断言支持率；拒答没有答案可评分。False Refusal 包含生成拒答与校验拦截，不能全部解释成校验器错误。

## 分块效应与选择范围

| 产生相同文本边界的配置 | Chunk 数 |
|---|---:|
| 450/0 | 100 |
| 450/60 | 100 |
| 900/0, 900/120, 1200/120, 1200/180 | 96 |

最佳 dev 得分用于冻结测试配置，不能据单次实验宣称普遍最优。相同边界配置间的得分差异不能归因于 Chunk Size/Overlap；本集仍需要真实长页资料补充。页级召回也不等于完整事实召回。

## Verifier 模型独立配置试验

同为 450/0 dev、strict、Luna 生成。每组各生成一次，答案不完全相同，保留随机性影响。

| Verifier | Correctness | False refusal | P50 / P95 ms | Mean USD/query |
|---|---:|---:|---:|---:|
| gpt-5.6-luna | 78.57% | 21.43% | 6866.2 / 11097.7 | 0.00086741 |
| gpt-4.1-mini | 80.95% | 19.05% | 5641.6 / 10082.1 | 0.00089413 |

该 pilot 证明可真实调用不同 Verifier，但不足以证明换模型必然改善；继续保留用户选择的 Luna/Luna 经济基线。

验证模式详见 [off / fast / strict 对比](verification/comparison.md)。Runtime off/fast 不提供语义支持保证；本轮不根据 test 结果继续修改提示词或选模型。

## 费用账本

| 实际运行报告 | USD |
|---|---:|
| [chunks-api/chunk-api-1200-120-dev.json](chunks-api/chunk-api-1200-120-dev.json) | 0.18900416 |
| [chunks-api/chunk-api-1200-180-dev.json](chunks-api/chunk-api-1200-180-dev.json) | 0.19583936 |
| [chunks-api/chunk-api-450-0-dev.json](chunks-api/chunk-api-450-0-dev.json) | 0.20311336 |
| [chunks-api/chunk-api-450-60-dev.json](chunks-api/chunk-api-450-60-dev.json) | 0.18791012 |
| [chunks-api/chunk-api-900-0-dev.json](chunks-api/chunk-api-900-0-dev.json) | 0.19426016 |
| [chunks-api/chunk-api-900-120-dev.json](chunks-api/chunk-api-900-120-dev.json) | 0.19017516 |
| [chunks-api/chunk-api-selected-test.json](chunks-api/chunk-api-selected-test.json) | 0.18892072 |
| [api-baseline-v1/chunk-api-900-120-dev.json](api-baseline-v1/chunk-api-900-120-dev.json) | 0.16256296 |
| [verifier-models/mini-450-0-dev.json](verifier-models/mini-450-0-dev.json) | 0.20190656 |
| [verification/off.json](verification/off.json) | 0.18726352 |
| [verification/fast.json](verification/fast.json) | 0.18226592 |
| [live-api-smoke.json](live-api-smoke.json) | 0.00026316 |
| [live-ui-smoke.json](live-ui-smoke.json) | 0.00132072 |

有记录的已知估算费用合计：USD **2.08480588**；费用完整：True。

包含独立 Judge、索引、诊断基线和失败补评；应用 cost/query 另见逐题报告，不能将评估开销当作用户每次问答费用。复用的 strict 报告和修复前快照不重复收费计数。

## 限制

- Synthetic multilingual policy corpus with related templates, not human-labeled production data.
- One run per configuration. Identical chunk layouts do not establish a chunk-size effect; API ranking/generation/Judge variation remains.
- Verifier pilot and mode comparison regenerate answers; not paired causal experiments.
- Judge judgments are automated. Citation scores apply to delivered answers only.
- Uniform configured prices and reported usage are estimates, not invoices. Failed original Judge cost is included in its repaired report; recovery snapshots and reused strict runs are not added twice.
