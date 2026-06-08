# Hermes / OpenClaw Integration Guide

## Goal

Connect the ChatGPT Visible Bridge Telegram Router to an existing OpenClaw or Hermes Telegram gateway, so that `/cgpt` messages are automatically routed to the local task queue without requiring a separate Telegram bot.

## Design Philosophy

- **Thin frontend**: The router is a thin layer that translates Telegram commands to local file operations. No heavy bot framework required.
- **Reuse existing infrastructure**: If you already have OpenClaw or Hermes receiving Telegram messages, add a simple prefix router to intercept `/cgpt` commands.
- **No credential duplication**: The router doesn't need its own Telegram token — it uses the existing gateway's message delivery mechanism.

## Integration Options

### Option A: OpenClaw Router Plugin (Recommended)

If OpenClaw supports custom router plugins or message interceptors, add a handler that checks for the `/cgpt` prefix:

```python
# In your OpenClaw router configuration or plugin
from chatgpt_visible_bridge.telegram import TelegramRouter

cgw_router = TelegramRouter()

def on_telegram_message(message_text: str) -> str | None:
    """Intercept /cgpt messages and route to CGW."""
    if not message_text.startswith("/cgpt"):
        return None  # Let other handlers process this message

    return cgw_router.route(message_text)
```

**Pros:**
- Reuses OpenClaw's Telegram connection
- No separate bot token needed
- Unified message flow

**Cons:**
- Requires OpenClaw plugin/extension capability
- Router logic runs in the OpenClaw process

### Option B: Hermes Message Router

If Hermes has a message routing system, add a rule that routes `/cgpt` prefix messages to the CGW handler:

```python
# Hermes router configuration (example)
from chatgpt_visible_bridge.telegram import TelegramRouter

cgw_router = TelegramRouter()

def handle_hermes_message(message: dict) -> dict:
    text = message.get("text", "")
    if not text.startswith("/cgpt"):
        return {"action": "pass"}  # Pass to next handler

    response = cgw_router.route(text)
    return {
        "action": "reply",
        "text": response,
    }
```

**Pros:**
- Integrates with Hermes' existing routing system
- Can combine with other Hermes handlers (e.g., `/life`, `/mine`)

**Cons:**
- Requires Hermes to support custom router rules

### Option C: Standalone Telegram Bot (Fallback)

If you don't have OpenClaw or Hermes, use a standalone bot script:

```python
#!/usr/bin/env python3
"""Minimal Telegram bot for CGW."""

import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from chatgpt_visible_bridge.telegram import TelegramRouter

router = TelegramRouter()

async def handle_cgpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = router.route(text)
    await update.message.reply_text(response, parse_mode="Markdown")

if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("cgpt", handle_cgpt))
    app.run_polling()
```

**Pros:**
- Works independently of OpenClaw/Hermes
- Full control over bot behavior

**Cons:**
- Requires separate bot token
- Needs to be hosted/running somewhere

## CGW_HOME Configuration

When integrating with OpenClaw or Hermes, ensure `CGW_HOME` is set correctly:

```bash
# In your OpenClaw/Hermes environment
export CGW_HOME=/home/conanxin/.openclaw/workspace/chatgpt-visible-bridge
```

The router will read/write tasks to this directory, which is the same directory used by the CLI worker.

## Message Flow

```
Telegram user sends /cgpt ask "review this"
         |
         v
    OpenClaw / Hermes receives message
         |
         v
    Prefix router detects /cgpt
         |
         v
    TelegramRouter.route("/cgpt ask review this")
         |
         v
    Creates inbox/<task_id>.json
         |
         v
    Returns formatted Telegram reply
         |
         v
    User sees: "✅ Task created: abc123..."
         |
         v
    User runs cgpt-worker-once --mock locally
         |
         v
    User sends /cgpt result abc123
         |
         v
    Router reads outbox/ + reports/ and replies
```

## Example OpenClaw Plugin (Conceptual)

```python
# plugins/cgw_router.py
from openclaw.plugins import MessagePlugin
from chatgpt_visible_bridge.telegram import TelegramRouter

class CGWRouterPlugin(MessagePlugin):
    name = "cgw_router"
    prefix = "/cgpt"

    def __init__(self):
        self.router = TelegramRouter()

    def handle(self, message: str) -> str | None:
        if not message.startswith(self.prefix):
            return None
        return self.router.route(message)
```

## Security Considerations

- The router **never** executes commands or starts the worker. It only creates/reads task files.
- The router does **not** store Telegram tokens. The parent gateway (OpenClaw/Hermes) manages authentication.
- All file operations are confined to `CGW_HOME`.
- Tasks are always created with `consult_only` and `allow_execute=false`.

## Testing the Integration

```bash
# 1. Set CGW_HOME
export CGW_HOME=/tmp/cgw-test

# 2. Simulate a Telegram message via CLI
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt ask Test integration"

# 3. Check the task was created
python3 -m chatgpt_visible_bridge.cli task-status

# 4. Run the worker
python3 -m chatgpt_visible_bridge.cli worker-once --mock

# 5. Query the result
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt result <task_id>"
```
