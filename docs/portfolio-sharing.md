# 求职作品的分享与部署

仓库展示、下载复现、受控在线 Demo 是三个独立入口。目前提供源码与可部署配置；尚未购买服务器或域名，没有公开在线地址。`127.0.0.1` 只能访问浏览器所在的机器。

## 给招聘方的入口

分享包含最新材料的 [项目分支](https://github.com/Twergu/My-portfolio/tree/codex/rag-quality-v2)，可从 README 查看真实截图、架构和最终 24 题结果。默认分支若未合并，根仓库首页可能仍是旧版。

- **30 秒**：README 顶部能力、截图、18/24 冻结结果和六个失败。
- **2 分钟**：[演示路线](demo-walkthrough.md)，看检索、物理页引用、工具证据与保守拒答。
- **深入检查**：[完整源码目录](../SOURCE_INDEX.md)、[架构决定](architecture.md)、[冻结评估](../reports/agent-freeze-20261005/acceptance.md)、[CI](https://github.com/Twergu/My-portfolio/actions/workflows/ci.yml)。

截图是已有真实界面的历史记录，带版本与限制说明；不把静态截图、Mock 日历或本地检索当成在线真实模型演示。不公开 API key、访客 token、私人文档或本机数据库。当前没有新增演示视频；可按演示路线录制。

## 无需额度的本地复现

安装 Git 与 Docker Compose，在空目录运行：

```sh
git clone --branch codex/rag-quality-v2 https://github.com/Twergu/My-portfolio.git
cd My-portfolio
docker compose up --build -d --wait
```

浏览器打开 `http://127.0.0.1:8000`，导入内置示例 PDF，体验原文检索和引用。默认是 local 开发模式，仅绑定回环地址；它不是公开 Demo。业务 Agent 需要配置真实模型 API，本地无额度模式不会伪造 Agent 输出。

## 有服务器后的部署流程

此流程针对单台 Linux 主机、一个 Uvicorn worker。准备 Docker Engine + Compose v2，将域名 A/AAAA 指向服务器，只将 TCP 80/443 对外开放。SSH 仅按自己的运维方式开放；数据库无需发布端口。不要将应用的 8000/18001 端口改为公网监听。若开启云代理/CDN，须先重新检查可信代理和真实 IP 配置，本模板默认直连 Caddy。

1. 克隆上述分支，复制 `.env.demo.example` 为 `.env.demo`，限制该文件的读取权限。

   ```sh
   cp .env.demo.example .env.demo
   chmod 600 .env.demo
   ```

2. 将 `RAG_DEMO_DOMAIN` 改为自己的域名，不含 `https://`、端口或路径。保留 `RAG_MODE=local` 可先验证部署；真实 Agent 设置 `RAG_MODE=api`，填入 API 地址、模型、服务器专用 API key，以及各模型的实际每百万 token 单价。推荐在供应商控制台另外设置额度/项目限额并核对其是否为硬限制。价格留空或为零时，本 Demo 拒绝收费调用。

3. 启动独立 Demo 项目；它有独立数据卷，不使用普通本地项目的数据。

   ```sh
   docker compose --env-file .env.demo -f compose.demo.yaml config --quiet
   docker compose --env-file .env.demo -f compose.demo.yaml up --build -d --wait
   ```

   不要在分享屏幕时运行没有 `--quiet` 的 `config` 命令，它可能展开密钥。Caddy 会在 DNS、80/443 可用时申请证书。CI 使用 localhost 的内部 CA 验证 HTTPS 链路，不代表已申请公网证书。

4. 初始化仓库内八页**虚构**政策，不读取自己的文档目录。

   ```sh
   # local 模式，无模型费用
   docker compose --env-file .env.demo -f compose.demo.yaml exec app python -m scripts.prepare_demo
   # api 模式时改用下面这一条，Embedding 会计费并经过预算守卫
   docker compose --env-file .env.demo -f compose.demo.yaml exec app python -m scripts.prepare_demo --live
   ```

   重复执行不会新增重复文档；Embedding 配置变化会重新索引。不要用此初始化命令处理其他正在使用的知识库。先初始化再发访客账号，避免维护与用户请求同时进行。

5. 为每位招聘方创建单独只读账号；令牌仅保存到私密文件，不打印到日志。

   ```sh
   docker compose --env-file .env.demo -f compose.demo.yaml exec app python -m scripts.manage_access create-user reviewer-01 --roles demo-reviewer --token-file /app/data/.secrets/reviewer-01.txt
   mkdir -p .secrets
   chmod 700 .secrets
   docker compose --env-file .env.demo -f compose.demo.yaml cp app:/app/data/.secrets/reviewer-01.txt .secrets/reviewer-01.txt
   chmod 600 .secrets/reviewer-01.txt
   ```

   通过私人渠道把 `https://你的域名` 与该令牌发给收件人；不要放进 README、URL 查询参数、公共 Issue 或截图。登录后以 HttpOnly / Secure / SameSite=Strict cookie 使用。令牌本身没有自动到期机制；结束展示后由管理员撤销。

   ```sh
   docker compose --env-file .env.demo -f compose.demo.yaml exec app python -m scripts.manage_access list-users
   docker compose --env-file .env.demo -f compose.demo.yaml exec app python -m scripts.manage_access disable-user USER_ID
   ```

6. 私下验证登录、引用 PDF、日文界面、Agent 和拒答提示。查看 `/api/health` 不需要令牌；其他数据依然经过 ACL。网页上传、重索引、配置修改、权限修改均关闭，即使使用管理员账号也一样。运维通过主机 CLI 完成。

## 限额与运行边界

| 项目 | 默认值 / 行为 |
|---|---|
| 单用户每日请求 | 20；新问题和每次澄清回复分别计数，失败请求也计数 |
| 全站每日请求 | 100；UTC 日期切换后恢复 |
| IP 请求 | 每分钟 10 次推理；登录另有每 IP 10 次 / 全站 60 次每分钟限制 |
| 同时推理 | 全站 2 个、每用户 1 个；繁忙时返回 429，不排长队 |
| 输入/输出 | HTTP 请求 64 KiB；模型请求序列化 UTF-8 最多 60,000 bytes；输出最多 4,096 tokens |
| 每日模型预算 | 默认 USD 1 的配置估算预算；每次 API 前预留，成功且用量可信才退回差额 |
| 失败/缺失用量 | 保留整笔预留；没有隐式 HTTP 重试；实际回报超出预留会阻断后续收费请求 |
| 重启 | 配额和预算保留在 app_data；Agent 的内存澄清会话丢失，需重新开始 |
| 规模 | 单进程；并发槽位不跨进程共享；不支持多副本或多 worker 部署 |

费用限制使用所配置单价、UTF-8 字节及协议余量估算输入上界，不是供应商账单级硬上限。输入 tokenizer、服务附加费用、错误价格、费用回报错误仍有风险；第一次异常超额响应只能事后熔断。供应商的独立额度限制仍应保留。预算守卫也会覆盖 Planner、Embedding、Generator、Verifier，不跳过 Strict 校验来省钱。

Demo 仍保留读取获授权文档/下载 PDF 的能力，所以只装载可公开的虚构资料。问题会发给配置的模型服务；不要输入真实公司或个人信息。运营日志与 Agent 输出可能含用户输入，保留在服务器，不能混进公开发布包。删除数据卷会清空配额、账号和预算，不应作为绕过限额的方法。

TLS 配置依据 [Caddy 自动 HTTPS](https://caddyserver.com/docs/automatic-https)；转发身份依据 [reverse_proxy 文档](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)。应用只信任固定代理 IP，Caddy 覆盖客户端伪造的 X-Forwarded-For；网段冲突时同步修改 `RAG_PROXY_SUBNET`、`RAG_PROXY_IP` 和 `RAG_APP_IP`，为两个容器分配不同的同网段地址。Compose 服务继承遵循 [Docker extends](https://docs.docker.com/compose/how-tos/multiple-compose-files/extends/)。

## 打包与复核

```sh
python -m scripts.source_index --archive
python -m scripts.release_check --git .
```

得到 `exports/knowbase-source-latest.zip` 与独立的 `exports/knowbase-release-check.json`；后者记录 ZIP SHA-256、文件数量、扫描范围及发现。扫描清单覆盖源码包、已知本地密钥值、常见密钥格式与所有可达 Git 历史对象，但不是渗透测试，也不保证识别未知格式或不可达历史。必须在最终文件确定后重新打包并扫描，校验报告不放入 ZIP 以避免自引用哈希。

仓库未指定通用开源许可证；公开供招聘方阅读不等于授予任意再分发许可。后续确定许可证时单独加入。GitHub Release 可在最终验收并决定版本号后发布 ZIP 与校验报告，目前不自动打 tag、合并 PR 或发布 Release。
