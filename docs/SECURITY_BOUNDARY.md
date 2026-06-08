# Security Boundary

## Trust Model

本项目设计为**个人本地使用**。用户是主要操作者，完全控制 worker 何时运行以及处理什么任务。

---

## 核心安全边界

### 1. /cgpt 命令 — 仅咨询（Consult-Only）

- `/cgpt` 创建的任务默认是 `consult_only` 模式。
- ChatGPT 生成的建议**只保存为文本，不自动执行**。
- 用户必须手动运行 `/agent approve` 才能进入执行阶段（MVP 不实现执行）。
- 执行阶段（如果未来实现）也必须：
  - `policy.allow_execute=true`
  - 用户显式确认
  - 每一步可中断、可审计

### 2. 不自动执行 ChatGPT 生成的命令

- Worker 不会解析或执行 ChatGPT 返回的任何命令、脚本或代码。
- 返回的文本保存在 `reports/` 和 `outbox/` 中，供用户阅读后**手动决定是否执行**。
- 即使 `policy.allow_execute=true`（未来实现），执行也必须通过独立的审批流程。

### 3. 不读取 Token / Cookie / Session

- 代码中**不读取** OpenAI API key、ChatGPT session token、浏览器 cookie。
- `.env` 文件在 `.gitignore` 中，不会被提交。
- `.env.example` 只包含占位符值，无真实凭证。
- Live adapter 未来需要凭证时，必须通过外部浏览器桥（如 codex-chatgpt-control）管理，不由本项目直接存储。

### 4. 不上传文件

- MVP 不实现文件上传功能。
- `policy.allow_upload_files` 存在但始终为 `false`。
- 即使未来实现，上传也必须是：
  - 用户显式选择文件
  - 确认上传目标和用途
  - 可审计的上传日志

### 5. 不常驻控制浏览器

- Worker 是 **one-shot**（处理完退出），不是常驻 daemon。
- 不启动常驻浏览器进程。
- 不维持浏览器 session。
- 未来 Live adapter 需要浏览器时：
  - 每次 worker 启动时独立启动浏览器实例
  - 处理完后关闭浏览器
  - 浏览器进程可见（用户可在任务管理器中看到）

### 6. Live Adapter 必须可见、可中断、可报告 Blocker

当未来接入真实 ChatGPT Web adapter 时，必须满足：

| 要求 | 说明 |
|------|------|
| **可见** | 浏览器操作对用户可见（headless 模式需要明确启用，默认 headful） |
| **可中断** | 用户可随时按 `Ctrl+C` 或关闭浏览器窗口中断任务 |
| **可报告** | 如果任务被阻塞（如验证码、登录态失效），adapter 必须报告 `blocked` 状态并记录原因 |
| **不自动重试** | 遇到 blocker 时不自动重试，等待用户介入 |
| **超时保护** | 单次任务设置硬超时（如 5 分钟），超时自动失败 |

---

## 其他边界

### 7. 文件系统隔离

- 所有运行时数据存储在 `CGW_HOME`（默认：`~/.openclaw/workspace/chatgpt-visible-bridge/`）。
- Worker 只读取 `inbox/` 和写入 `active/`、`outbox/`、`failed/`、`reports/`。
- 不操作工作目录之外的文件。

### 8. Telegram 约束

- Telegram 是**可选通知层**，不是控制平面。
- 不硬编码 bot token 或 chat_id。
- Telegram bot（如果实现）只读写本地文件，不执行命令。

### 6. Live Adapter 安全约束（CGW-3B）

- **默认 blocked**：`codex-chatgpt-control` adapter 未显式启用 live 时返回 `blocked/live_not_enabled`，不操作真实 ChatGPT Web。
- **显式 one-shot**：真实 live smoke 需要 `CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1` 或 CLI `--live`，并通过手动 `worker-once` 触发。
- **兼容 host 要求**：真实 live smoke 必须在支持 Codex/browser bridge 的 host 中运行；普通 shell 下 `dependency_missing` 或 `browser_bridge_unavailable` 是预期 blocker。
- **不上传/下载文件**：CGW-3B live adapter 只提交纯文本 prompt 并读取 Markdown 回复。
- **不读取 cookie/session/profile/token**：登录态由外部可见浏览器和 `codex-chatgpt-control` 管理，本项目不读取或打印浏览器凭证。
- **不硬编码 selectors**：本项目不内置 ChatGPT DOM selector scraping 或私有接口调用。
- **不自动执行返回内容**：ChatGPT 返回的 Markdown 只写入 `outbox/` 和 `reports/`。
- **失败写 blocker**：遇到依赖缺失、桥不可用、登录要求、权限要求或 UI 状态不可读时，必须写入结构化 blocked result 和 next action。

---

## 威胁模型

| 威胁 | 缓解措施 |
|------|----------|
| 意外自动执行 | Consult-only 默认；无执行代码在 MVP 中 |
| 凭证泄露 | `.env` 在 `.gitignore`；无真实 token 在 repo 中 |
| 远程命令注入 | 无网络监听；CLI 只读写本地文件 |
| 权限提升 | 以当前用户运行；无 sudo 或 setuid |
| 数据外泄 | MVP 无网络调用；本地文件系统 only |
| 浏览器被劫持 | 浏览器实例每次独立启动、处理完关闭 |
| 任务卡死 | 硬超时；用户可中断；blocker 报告 |
| 真实 ChatGPT 误操作 | CGW-3B 默认 blocked；真实 live smoke 需要显式启用且只处理 one-shot |

---

## 未来扩展的安全检查清单

在添加以下功能前，必须通过安全审查：

- [ ] **Live adapter**：可见、可中断、可报告 blocker、超时保护
- [ ] **Telegram bot**：只读文件，不执行命令，token 不在 repo 中
- [ ] **执行模式**：独立审批流程、每步确认、可回滚
- [ ] **文件上传**：用户显式选择、确认目标、可审计日志
- [ ] **Watch 模式**：非默认，需用户明确启用，有日志和超时

---

## 报告安全问题

如发现安全漏洞，请开 private issue 或邮件联系维护者。不要公开披露安全漏洞。
