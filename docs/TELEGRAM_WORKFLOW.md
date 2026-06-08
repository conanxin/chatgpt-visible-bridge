# Telegram Workflow

## 定位

Telegram 是**可选通知与查询层**，不是核心引擎。整个 pipeline 通过 CLI 和本地文件运行。Telegram 只是提供了一个方便的查询入口。

## 当前状态

✅ **Telegram Router 已实现**（CGW-2）。模块位于 `chatgpt_visible_bridge/telegram/`，支持命令解析、处理、格式化，无需真实 Telegram API 即可测试。

## 命令设计

| 命令 | 说明 | 等效 CLI | 状态 |
|------|------|----------|------|
| `/cgpt ask <prompt>` | 创建咨询任务（consult-only） | `cgpt-create-task --prompt "..."` | ✅ CGW-2 已实现 |
| `/cgpt status` | 显示队列状态 | `cgpt-task-status` | ✅ CGW-2 已实现 |
| `/cgpt result <task_id>` | 显示任务结果和报告 | `cgpt-task-result <task_id>` | ✅ CGW-2 已实现 |
| `/cgpt show <task_id>` | 显示任务详情和原始 prompt | `cgpt-task-show <task_id>` | ✅ CGW-2 已实现 |
| `/cgpt help` | 显示使用帮助 | — | ✅ CGW-2 已实现 |
| `/cgpt review <task_id>` | 查看任务报告和建议 | — | 未来（同 result） |
| `/cgpt next` | 执行建议的下一步 | — | 未来（需 `/agent approve`） |
| `/agent approve <task_id>` | 批准执行任务建议 | — | **MVP 不实现** |

## 数据流

```
用户在 Telegram 发送 /cgpt ask "分析这个架构"
         ↓
    Telegram Router 解析命令 → 创建 inbox/<task_id>.json
         ↓
    用户收到确认："✅ Task created: abc123 [pending]"
         ↓
用户在本地运行 cgpt-worker-once --mock
         ↓
    Worker 处理 → 写 reports/ + outbox/
         ↓
用户在 Telegram 发送 /cgpt result abc123
         ↓
    Telegram Router 读取 outbox/ + reports/，回复结果
         ↓
用户看到结构化报告，手动决定是否执行建议
```

## 约束

- **不自动执行**：`/cgpt` 命令始终创建 `consult_only` 任务。
- **不存储凭证**：Telegram bot token 在 `.env` 中，不在代码里。
- **不硬编码 chat_id**：从环境变量读取 `TELEGRAM_CHAT_ID`。
- **不执行命令**：Router 只读写本地文件，不运行 shell 命令或脚本。
- **个人使用**：设计为单用户或小组使用，非生产级 bot。

## 实现方式

### 方式 1：OpenClaw / Hermes Telegram Gateway（推荐）

复用已有的 OpenClaw Telegram 集成，添加一个 prefix router 拦截 `/cgpt` 命令：

```python
from chatgpt_visible_bridge.telegram import TelegramRouter

router = TelegramRouter()

# 在 OpenClaw 消息处理中
def on_telegram_message(text: str) -> str | None:
    if not text.startswith("/cgpt"):
        return None  # 让其他 handler 处理
    return router.route(text)
```

详见 [HERMES_INTEGRATION.md](HERMES_INTEGRATION.md)。

### 方式 2：独立 Telegram Bot

如果未使用 OpenClaw/Hermes，可用 `python-telegram-bot` 或 `aiogram` 实现独立 bot：

```python
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from chatgpt_visible_bridge.telegram import TelegramRouter

router = TelegramRouter()

async def handle_cgpt(update: Update, context):
    response = router.route(update.message.text)
    await update.message.reply_text(response, parse_mode="Markdown")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("cgpt", handle_cgpt))
app.run_polling()
```

### 方式 3：CLI 开发测试

无需 Telegram bot token，直接用 CLI 模拟：

```bash
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt ask Hello world"
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt status"
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt result <task_id>"
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt show <task_id>"
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt help"
```

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
