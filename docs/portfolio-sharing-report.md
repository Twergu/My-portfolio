# 求职作品分享与可部署版本：Modification Report

日期：2026-10-07。目标是准备可复现、受控的分享版本；用户尚无服务器或域名。本轮不部署公网、不新跑付费的 24 题评估、不修改 Agent/RAG 提示与原始失败记录。

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

本地安全/访问/初始化回归通过；没有本地 PostgreSQL 服务的项目明确标为 skipped，将由真实 GitHub Actions pgvector 服务执行。前端全部通过，Ruff lint / format 通过。完整 CI 的结果与测试数量以同版本机器报告为准，完成后追加到本节。

发布前执行 `python -m scripts.source_index --archive` 和 `python -m scripts.release_check --git .delivery/My-portfolio`。独立 `exports/knowbase-release-check.json` 记录最终 ZIP SHA-256 和扫描范围，不纳入 ZIP 本身。

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
