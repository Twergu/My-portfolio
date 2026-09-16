# 本轮 12 项修改与验证

本轮实现与上轮记录分开；原始实验报告保留。人工审核、Agent、人在回路按最新指示暂缓。

| 项目 | 实现方向与效果 | 验证入口 |
|---|---|---|
| 1 Hybrid Retrieval | Dense + SQLite BM25 / PostgreSQL Full-text，Top 20 后 RRF；数字/日期/政策编号和中日文共同分析器 | `tests/test_stores.py`、[真实三路实验](../reports/v3/retrieval.json) |
| 2 Reranker | 独立可配置 LLM 模型，对候选完整重排，Top 5 交给 Generator；格式失败最多修复一次，失败与全部成本可见 | `tests/test_retrieval.py`；真实 test Recall@5 88.1%→100%，但检索 P50 0.46→6.16 秒 |
| 3 Verifier 校准 | 36 条中日英 Claim/Evidence，supported/unsupported/partial/数字/否定/税额/版本/例外；开发和测试各半 | [校准数据](../evals/claim_calibration.json)、[开发对照](../reports/v3/calibration-calibrated-dev.json)、[测试](../reports/v3/calibration-calibrated-test.json)；dev 两个提示词均 Precision=1、Recall=6/7；校准 test 18/18；不宣称普遍改善 |
| 4 Verification 策略 | off/fast/strict 保留；新增 all/selective；严格限制可跳过的简单原文摘录，未检查项保持 unknown | `tests/test_verifier_calibration.py`；59 条生成断言的离线回放中 0 条可跳过，未测得节省；默认 all |
| 5 Human-reviewed set | 用户明确暂缓；不伪造人工审核标签 | 所有数据集明确来源，后续由业务审核人确认 |
| 6 Metadata / Version | 独立 policy_status、生效日期、失效日期、部门、版本；SQL 解析范围后才搜索；中日文筛选与编辑界面 | `tests/test_stores.py` 日期边界、草案/旧版/未分类、过滤为空；[使用说明](access-control.md) |
| 7 ACL | User、Role、Document Permission、所有者；required 模式验证真实服务器身份；覆盖两路检索、文件、列表、修改、设置；迁移 SQLite 到 PG 时保留身份、权限与版本信息 | SQLite/PG 共用权限测试 + HTTP 越权与模型调用隔离测试；[浏览器只读账号验收](../reports/v3/browser-access.json)；默认 local 明确为单用户开发模式 |
| 8 HNSW | Exact 默认；真实索引计划、Recall≥95%、P95 更快才进入人工评估候选，不自动切换 | `backend/search_policy.py` 与 scale benchmark `ann_acceptance`；合成实验不代表生产权限过滤场景 |
| 9 Latency / Cost | 分离 query embedding/retrieval/reranking/generation/verification；角色 tokens、已知/未知成本，真实完整 RAG 对比；增加逐题断点保存，重启记录额外索引成本 | [strict / fast 实测](../reports/v3/summary.md)：P50 13.90 / 10.50 秒，平均 USD 0.002028 / 0.001694；失败尝试不隐藏、独立 Judge 费用不混入 app/query |
| 10 质量/可维护性 | Ruff E/F/I/B、格式检查、pytest-cov 分支覆盖率进入 CI；Provider/Verifier/Reranker/治理逻辑集中 | [最新 CI](../reports/ci-status.json)、[全部测试动态报告](../reports/ci/tests.md)、[含 PostgreSQL 覆盖率](../reports/ci/coverage.json)；mypy 后续按类型接口逐步引入 |
| 11 Agent | 按依赖顺序暂缓 LangGraph，不提前增加多 Agent | [上线前条件](adr/0003-agent-gates.md) |
| 12 Human-in-the-loop | 本轮不暴露真实操作工具；未来审批必须绑定可审核的准确参数与有效权限 | 同上；当前没有已实现的操作审批或用户审计功能 |

配置与复现：

```bash
python -m scripts.retrieval_experiment
python -m scripts.calibrate_verifier --split dev --prompt baseline --output reports/v3/calibration-baseline-dev-live.json
python -m scripts.calibrate_verifier --split dev --prompt calibrated --output reports/v3/calibration-calibrated-dev.json
python -m scripts.calibrate_verifier --split test --prompt calibrated --output reports/v3/calibration-calibrated-test.json
python -m scripts.evaluate --mode api --split test --overlap 0 --retrieval-mode hybrid --reranker-mode llm --verification-mode strict --judge-model gpt-4.1 --concurrency 2 --output reports/v3/quality-strict-test
python -m scripts.evaluate --mode api --split test --overlap 0 --retrieval-mode hybrid --reranker-mode llm --verification-mode fast --judge-model gpt-4.1 --concurrency 2 --output reports/v3/quality-fast-test
python -m scripts.v3_results
python -m ruff check .
python -m ruff format --check .
python -m scripts.check
```

这些 API 命令会使用配置的付费模型。三路检索使用同一索引，每个方案真实调用查询 Embedding；初次开发集有 1 次重排 schema 失败，报告保留且整体状态未伪装为全通过。测试集三组各 54 题均无失败。已有 test 集用于回归，不能再次宣称全新未见测试集。

## 实际收益与保留的限制

Hybrid 单独使用时，Recall@1 从 58.33% 升至 63.10%，但 Recall@5 仍是 88.10%。加入 LLM Reranker 后 Recall@1 为 73.81%、Recall@3/5 为 100%、MRR 为 0.9643、nDCG 为 0.9736。这证明本数据集上的主要排序收益来自重排；不能把组合收益全部归给 Hybrid。

完整 RAG 的 strict / fast 分别完成 54 题，没有 API 或 Judge 格式错误残留。Answer Correctness 为 90.48% / 92.86%，Refusal Accuracy 为 92.59% / 96.30%，可回答问题的未交付率为 9.52% / 4.76%。引用有据的自动评分均为 100%，分母分别为 38 / 40 个已交付答案。该分数不是可靠性保证：已发现 Judge 既有漏判，也有误判，详见 [逐例诊断](../reports/v3/grounding-diagnostics.md)。

这次独立运行中，fast 的 P50 比 strict 低 24.5%，平均应用成本低 16.5%，代价是没有运行时语义 Verifier。两轮生成和重排存在随机性，不能解释为纯粹关闭 Verifier 的因果收益。strict 的 Reranker P50 约 6.78 秒，Generator 约 4.14 秒，Verifier 约 2.50 秒，而实际数据库检索仅约 0.016 秒；阶段分位数不能直接相加。后续延迟优化应首先针对重排与生成。

默认继续使用 Exact、Dense、关闭付费 Reranker、strict/all 和 baseline Verifier 提示词。高召回配置需要在模型设置中选择 hybrid + llm；Verifier/Reranker 可分别指定模型，但本轮没有实测更轻量的独立 Verifier，也不声称该项已降低成本。

两次真实 CI 都执行了全部数据库测试及 1k/10k/100k 实验。HNSW 在 10k、ef=400 的 Recall 为 95% / 91%，100k、ef=1000 为 57% / 67%；索引构建与共享 runner 存在波动。保留 [第一次原始结果](../reports/v3/ci-first/README.md) 和 [最终复验](../reports/vector-scale.md)，不把某一次达标当成稳定保证。

本轮完整、可追溯实验估算费用小计 USD 0.662463，包含索引、检索、校准和两轮额外 Judge。此前中断运行的实际用量未知，单独记录在 [中断说明](../reports/v3/interrupted-quality-run.json)，没有计作零，也没有推算质量。原始输出不因后续诊断而改分。
