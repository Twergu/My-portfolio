# 求职作品分享与可部署版本：Modification Report

实施：2026-10-07；验收归档：2026-10-08。目标是准备可复现、受控的分享版本；用户尚无服务器或域名。本轮不部署公网、不新跑付费的 24 题评估、不修改 Agent/RAG 提示与原始失败记录。

## 修改内容

| 文件 | 修改与效果 |
|---|---|
| `backend/demo_security.py` | 独立 DemoGuard / DemoProvider；日配额、登录限流、并发槽位、原子持久化费用预留；未知用量不退回、超额熔断、关闭隐式重试 |
| `backend/main.py` | Demo 强制 required 身份认证与 Strict/all；只读 HTTP 操作；域名白名单、HTTPS、请求体限制；所有推理入口（含澄清回复）纳入限额；保留 ACL 和同源 PDF 引用 |
| `dist/governance.js`, `dist/styles.css` | 中日文只读演示/虚构资料/隐私提示；隐藏上传与重建入口，显示文件位于演示服务器 |
| `compose.demo.yaml`, `deploy/Caddyfile`, `.env.demo.example` | 独立 Compose 项目、Caddy HTTPS、固定可信代理 IP、非公开数据库、loopback 应用端口、资源与日志限制；模板没有真实密钥 |
| `scripts/prepare_demo.py` | 幂等导入八页虚构政策，只对 `demo-reviewer` 角色授权；API 索引须显式 `--live`，经过同一预算 Provider |
| `scripts/demo_smoke.py`, `.github/workflows/ci.yml` | 增加真实 Docker / HTTPS / pgvector / 登录 cookie / 只读 / ACL / 请求限额 / 伪造 XFF / 重启持久性验收；不调用付费模型 |
| `tests/test_demo_security.py`, `tests/test_release_check.py`, `tests/frontend/demo.test.cjs` | 新增守卫、费用估算、异常、跨日/重启、权限及中日文 UI 回归；模型传输使用显式 MockTransport，不冒充真实 API |
| `tests/conftest.py` | 单元测试不继承操作者的 Demo / 域名配置或 API key |
| `scripts/release_check.py`, `scripts/source_index.py`, `.gitignore` | 检查源码 ZIP / 可达 Git 历史、私密路径、已知及常见密钥；补齐部署文件打包；排除 `.env.*`，仅纳入 example 模板 |
| `README.md`, `SECURITY.md`, `docs/portfolio-sharing.md`, `docs/demo-walkthrough.md` | 首页架构和真实截图、诚实的冻结指标、部署/账号签发撤销/预算边界、源码包校验和两分钟演示路线 |

## 验证记录

部署代码版本 `e603ef2cb38a8a8d74695a2f28d6d3cebd56aff0` 的 [完整 CI 37615440769](https://github.com/Twergu/My-portfolio/actions/runs/37615440769) 全绿。以下数量由下载的 JUnit / JSON 交叉核对，后续提交仅归档说明与报告，不改运行代码。

| 验证 | 实际结果 / 证据 |
|---|---|
| 完整 Python 回归 | **371 passed，0 failed，0 errors，0 skipped**；[机器报告](../reports/portfolio-sharing/ci-final/tests.md) |
| 真实 PostgreSQL + pgvector | **39 个用例实际执行通过**；[逐项清单及 JUnit 哈希](../reports/portfolio-sharing/ci-final/postgres-tests.json) |
| 前端 / Ruff | **17/17 前端通过**；lint / format 通过；[前端报告](../reports/portfolio-sharing/ci-final/frontend-tests.json)、[完整 CI 元数据](../reports/portfolio-sharing/ci-final/provenance.json) |
| 原 Docker 回归 | 构建、健康、PDF 引用与重启后数据保留通过；[验收记录](../reports/portfolio-sharing/ci-final/container-persistence.json) |
| 新 HTTPS Demo | Caddy TLS 证书验证、pgvector、登录及 Secure/HttpOnly/SameSite cookie、只读操作、跨来源拒绝、ACL 前置过滤和请求配额通过；[首次运行](../reports/portfolio-sharing/ci-final/demo-initial.json) |
| 重启 / 伪造 IP | 文档与配额保留；伪造 X-Forwarded-For 不能绕过登录 IP 限流；[重启记录](../reports/portfolio-sharing/ci-final/demo-restart.json) |
| Exact / HNSW 规模基准 | 1k / 10k / 100k 完整执行；[原始结果](../reports/portfolio-sharing/ci-final/vector-scale.md) |
| 冻结内容 | 原 24 题原始报告 SHA-256 不变；Agent、RAG、Provider、Grounding 与数据集无改动；[核对记录](../reports/portfolio-sharing/frozen-integrity.json) |

HTTPS 验收使用 localhost 内部 CA，验证了真实 TLS 链路与证书信任；它不是公网域名证书验收。Docker 使用真实 PostgreSQL 和本地检索，不调用付费模型；Provider 配额测试使用 MockTransport。不能把这些当成新增 Demo 限额下的真实模型质量实验。本地运行因缺少 PostgreSQL 的 39 个 skipped 已在上述 CI 中全部实际执行。

首次 [CI 37614252600](https://github.com/Twergu/My-portfolio/actions/runs/37614252600) 的完整测试、原 Docker 与规模基准通过，但新 HTTPS Demo 未通过：应用在代理启动前动态取得 `172.30.48.2`，与代理固定 IP 冲突。已为应用指定不同的固定 IP，并把 Demo 验收提前到耗时的 100k 基准之前；没有删除失败运行或省略测试。

发布前执行 `python -m scripts.source_index --archive` 和 `python -m scripts.release_check --git .delivery/My-portfolio`。独立 `exports/knowbase-release-check.json` 记录最终 ZIP SHA-256 和扫描范围，不纳入 ZIP 本身。

已扫描源码包与可达 Git 历史文件对象，没有发现本地已知密钥、所列常见密钥格式或禁止的私密路径；精确文件数、历史对象数、扫描范围及 SHA-256 以最终独立校验 JSON 为准。源码包包括源码、部署模板、测试、评估数据和历次报告，排除 `.env`、真实账号数据库、上传资料、日志和虚拟环境。

## 模型质量、性能与费用

冻结报告 `reports/agent-freeze-20261005/` 保持原始结果：版本 `9af3637`，Task Success 18/24，Correctness/Grounded 13/18，P50/P95 12.189/24.922 秒，配置估算 USD 0.002579/task；六个失败均保留。部署层是此后的改动，这些数字不是新增限额配置下的重新测量。

本轮未测量真实模型的新延迟或质量，不能宣称变快。Demo 限制上下文与输出，可能增加拒答/截断；严格证据校验仍然运行。费用守卫是基于操作者单价的保守估算与事后异常熔断，不能代替供应商硬额度。

## 尚存边界

- 尚未有服务器、域名或公网证书；本轮交付可部署配置与验证结果，不提供虚构在线 URL。
- 单进程 / 一个 worker；Agent 澄清会话不持久化，重启后需重开；请求配额和预算则持久化。活跃模型 HTTP 请求不能强制撤回。
- 访客令牌需私下提供和人工撤销；当前没有账号自助注册、SSO 或令牌自动过期。
- 文档只装载可公开的虚构样例；获授权用户可查看/下载原文。日历仍为 Mock，不构成审批。
- 安全扫描覆盖已知值及特定格式，不能保证识别所有泄露，也不是第三方安全审计。
- 演示路线已提供；没有新增录屏视频。GitHub Release / tag / 合并 PR / 许可证选择留待发布时决定。
