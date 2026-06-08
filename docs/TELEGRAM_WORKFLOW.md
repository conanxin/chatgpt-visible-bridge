# Telegram Workflow

## 定位

Telegram 是**可选通知与查询层**，不是核心引擎。整个 pipeline 通过 CLI 和本地文件运行。Telegram 只是提供了一个方便的查询入口。

## 未来 Telegram 命令设计

> **注意：以下命令是未来规划，MVP 阶段仅实现 CLI 等效命令。**

### 创建任务

| 命令 | 说明 | 等效 CLI |
|------|------|----------|
| `/cgpt ask <prompt>` | 创建咨询任务（consult-only） | `cgpt-create-task --prompt "..."` |
| `/cgpt review <task_id>` | 查看任务报告和建议 | `cgpt-task-show <task_id>` + `cgpt-task-result <task_id>` |
| `/cgpt next` | 执行建议的下一步（如果存在） | （未来：需 `/agent approve`） |

### 查询状态

| 命令 | 说明 | 等效 CLI |
|------|------|----------|
| `/cgpt status` | 显示队列状态（pending/active/completed/failed） | `cgpt-task-status` |
| `/cgpt result <task_id>` | 显示任务结果和报告 | `cgpt-task-result <task_id>` |

### 执行控制

| 命令 | 说明 | 状态 |
|------|------|------|
| `/agent approve <task_id>` | 批准执行任务建议（需 `allow_execute=true`） | **MVP 不实现** |
| `/agent cancel <task_id>` | 取消 pending 任务 | **MVP 不实现** |

## 数据流

```
用户在 Telegram 发送 /cgpt ask "分析这个架构"
         ↓
    Bot 在本地创建 inbox/<task_id>.json
         ↓
    用户收到确认："Task created: abc123 [pending]"
         ↓
用户在本地运行 cgpt-worker-once --mock
         ↓
    Worker 处理 → 写 reports/ + outbox/
         ↓
用户在 Telegram 发送 /cgpt result abc123
         ↓
    Bot 读取 outbox/ + reports/，回复结果
         ↓
用户看到结构化报告，手动决定是否执行建议
```

## 约束

- **不自动执行**：`/cgpt` 命令始终创建 `consult_only` 任务。
- **不存储凭证**：Telegram bot token 在 `.env` 中，不在代码里。
- **不硬编码 chat_id**：从环境变量读取 `TELEGRAM_CHAT_ID`。
- **不执行命令**：Bot 只读写本地文件，不运行 shell 命令或脚本。
- **个人使用**：设计为单用户或小组使用，非生产级 bot。

## 实现说明

MVP 不包含 Telegram bot 实现。它可以通过以下方式接入：

1. **OpenClaw / Hermes Telegram Gateway**：如果用户已有 OpenClaw Telegram 集成，可以写一个 router 将 `/cgpt` 命令映射到 CLI 调用。
2. **独立 Bot**：用 `python-telegram-bot` 或 `aiogram` 实现，读写同样的 JSON 文件。

Bot 应该只是一个**薄前端**，核心逻辑全部复用 CLI 的 Python 模块。

## 示例交互

```
User: /cgpt status
Bot:  📊 Queue Status
       Inbox: 2 pending
       Active: 0
       Outbox: 5 completed

User: /cgpt ask "请帮我 review 这个 PR 的架构"
Bot:  ✅ Task created: a1b2c3d4e5f67890
       Status: pending
       Run `cgpt-worker-once --mock` to process.

[用户本地运行 cgpt-worker-once --mock]

User: /cgpt result a1b2c3d4e5f67890
Bot:  📄 Result for a1b2c3d4e5f67890
       Status: success
       Adapter: mock

       ## 任务理解
       ...

       Report: reports/a1b2c3d4e5f67890.md
```
