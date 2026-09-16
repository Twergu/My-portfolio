# 本轮 12 项修改与验证

本轮实现与上轮记录分开；原始实验报告保留。人工审核、Agent、人在回路按最新指示暂缓。

| 项目 | 实现方向与效果 | 验证入口 |
|---|---|---|
| 1 Hybrid Retrieval | Dense + SQLite BM25 / PostgreSQL Full-text，Top 20 后 RRF；数字/日期/政策编号和中日文共同分析器 | `tests/test_stores.py`、[真实三路实验](../reports/v3/retrieval.json) |
| 2 Reranker | 独立可配置 LLM 模型，对候选完整重排，Top 5 交给 Generator；格式失败最多修复一次，失败与全部成本可见 | `tests/test_retrieval.py`；真实 test Recall@5 88.1%→100%，但检索 P50 0.46→6.16 秒 |
| 3 Verifier 校准 | 36 条中日英 Claim/Evidence，supported/unsupported/partial/数字/否定/税额/版本/例外；开发和测试各半 | [校准数据](../evals/claim_calibration.json)、[开发对照](../reports/v3/calibration-calibrated-dev.json)、[测试](../reports/v3/calibration-calibrated-test.json)；dev 两个提示词均 Precision=1、Recall=6/7；校准 test 18/18；不宣称普遍改善 |
| 4 Verification 策略 | off/fast/strict 保留；新增 all/selective；严格限制可跳过的简单原文摘录，未检查项保持 unknown | `tests/test_verifier_calibration.py`；实际覆盖率、成本随后由结果脚本统计；默认 all |
| 5 Human-reviewed set | 用户明确暂缓；不伪造人工审核标签 | 所有数据集明确来源，后续由业务审核人确认 |
| 6 Metadata / Version | 独立 policy_status、生效日期、失效日期、部门、版本；SQL 解析范围后才搜索；中日文筛选与编辑界面 | `tests/test_stores.py` 日期边界、草案/旧版/未分类、过滤为空；[使用说明](access-control.md) |
| 7 ACL | User、Role、Document Permission、所有者；required 模式验证真实服务器身份；覆盖两路检索、文件、列表、修改、设置 | SQLite/PG 共用权限测试 + HTTP 越权与模型调用隔离测试；默认 local 明确为单用户开发模式 |
| 8 HNSW | Exact 默认；真实索引计划、Recall≥95%、P95 更快才进入人工评估候选，不自动切换 | `backend/search_policy.py` 与 scale benchmark `ann_acceptance`；合成实验不代表生产权限过滤场景 |
| 9 Latency / Cost | 分离 query embedding/retrieval/reranking/generation/verification；角色 tokens、已知/未知成本，真实完整 RAG 对比 | `reports/v3/`；失败尝试不隐藏、独立 Judge 费用不混入 app/query |
| 10 质量/可维护性 | Ruff E/F/I/B、格式检查、pytest-cov 分支覆盖率进入 CI；Provider/Verifier/Reranker/治理逻辑集中 | `.github/workflows/ci.yml`、`reports/coverage.json`；mypy 后续按类型接口逐步引入 |
| 11 Agent | 按依赖顺序暂缓 LangGraph，不提前增加多 Agent | [上线前条件](adr/0003-agent-gates.md) |
| 12 Human-in-the-loop | 本轮不暴露真实操作工具；未来审批必须绑定可审核的准确参数与有效权限 | 同上；当前没有已实现的操作审批或用户审计功能 |

配置与复现：

```bash
python -m scripts.retrieval_experiment
python -m scripts.calibrate_verifier --split dev --prompt baseline --output reports/v3/calibration-baseline-dev-live.json
python -m scripts.calibrate_verifier --split dev --prompt calibrated --output reports/v3/calibration-calibrated-dev.json
python -m scripts.calibrate_verifier --split test --prompt calibrated --output reports/v3/calibration-calibrated-test.json
python -m scripts.evaluate --mode api --split test --overlap 0 --retrieval-mode hybrid --reranker-mode llm --verification-mode strict --judge-model gpt-4.1 --concurrency 2 --output reports/v3/quality-strict-test
python -m ruff check .
python -m ruff format --check .
python -m scripts.check
```

这些 API 命令会使用配置的付费模型。三路检索使用同一索引，每个方案真实调用查询 Embedding；初次开发集有 1 次重排 schema 失败，报告保留且整体状态未伪装为全通过。测试集三组各 54 题均无失败。已有 test 集用于回归，不能再次宣称全新未见测试集。
