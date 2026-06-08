# Telegram Router for ChatGPT Visible Bridge

## Overview

The Telegram Router (`chatgpt_visible_bridge.telegram`) provides a clean, testable layer that translates Telegram `/cgpt` commands into operations on the local task queue. It is **not** a Telegram bot — it is a command parser and handler library that can be used by:

1. A standalone Telegram bot script (Python `python-telegram-bot`, `aiogram`, etc.)
2. An OpenClaw / Hermes router plugin that intercepts `/cgpt` messages
3. The CLI `telegram-router` command for developer testing

## Architecture

```
Telegram message (e.g., "/cgpt ask Review this")
         |
         v
  +---------------+
  |   parser.py   |  <-- Extracts command + args
  +---------------+
         |
         v
  +---------------+
  |  handler.py   |  <-- Reads/writes task queue files
  +---------------+
         |
         v
  +---------------+
  | formatter.py  |  <-- Formats Telegram-friendly text
  +---------------+
         |
         v
  Telegram-friendly response string
```

## Module Breakdown

### parser.py

Parses raw Telegram text into structured `TelegramCommand` objects.

```python
from chatgpt_visible_bridge.telegram import parse_command, TelegramCommandType

cmd = parse_command("/cgpt ask Review the architecture")
assert cmd.type == TelegramCommandType.ASK
assert cmd.prompt == "Review the architecture"
```

### handler.py

Connects parsed commands to the file-based task queue. Creates tasks, reads status, retrieves results, and shows task details.

```python
from chatgpt_visible_bridge.telegram import TelegramHandler

handler = TelegramHandler()
response = handler.handle(cmd)  # Returns Telegram-friendly string
```

### formatter.py

Converts structured data into Telegram-formatted text (emoji, bullet lists, no markdown tables).

```python
from chatgpt_visible_bridge.telegram import format_status, format_result
```

### router.py

One-liner convenience: `parse + handle + format` in one call.

```python
from chatgpt_visible_bridge.telegram import TelegramRouter

router = TelegramRouter()
response = router.route("/cgpt ask Hello world")
```

## Supported Commands

| Command | Behavior | Policy |
|---------|----------|--------|
| `/cgpt ask <prompt>` | Creates a `consult_only` task in `inbox/` | `allow_execute=false`, `allow_upload_files=false` |
| `/cgpt status` | Shows queue counts + recent task IDs | Read-only |
| `/cgpt result <task_id>` | Shows result summary + report path | Read-only |
| `/cgpt show <task_id>` | Shows task metadata + original prompt | Read-only |
| `/cgpt help` | Shows usage instructions | Read-only |
| Unknown / invalid | Returns error + help text | No-op |

## Security Constraints

- **Consult-only by default**: All `/cgpt ask` tasks create `consult_only` tasks with `allow_execute=false` and `allow_upload_files=false`.
- **No automatic execution**: The router never runs worker processes or executes commands.
- **No credential access**: The router does not read or transmit Telegram tokens, API keys, or session data.
- **File-system only**: All operations are confined to `CGW_HOME`.

## CLI Testing

You can test the router without a real Telegram bot:

```bash
# Create a task via Telegram command simulation
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt ask Review the architecture"

# Check status
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt status"

# Run the worker
python3 -m chatgpt_visible_bridge.cli worker-once --mock

# Get result
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt result <task_id>"

# Show task details
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt show <task_id>"

# Help
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt help"
```

## Integration with Telegram Bot

To integrate with a real Telegram bot (e.g., `python-telegram-bot`), use the router as the core handler:

```python
from chatgpt_visible_bridge.telegram import TelegramRouter

router = TelegramRouter()

def handle_message(text: str) -> str:
    return router.route(text)

# In your bot handler:
# await update.message.reply_text(handle_message(update.message.text))
```

## Integration with OpenClaw / Hermes

See [HERMES_INTEGRATION.md](HERMES_INTEGRATION.md) for how to wire this router into an OpenClaw or Hermes Telegram gateway.
