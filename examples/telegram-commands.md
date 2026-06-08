# Telegram Commands Reference

> These are **simulated** commands for the Telegram Router. They can be tested via the CLI `telegram-router` command or integrated into a real Telegram bot / OpenClaw gateway.

## `/cgpt ask <prompt>`

Create a consult-only task from Telegram.

**Example:**
```
/cgpt ask 分析这个开源项目的架构并给出改进建议
```

**Behavior:**
- Creates a task JSON in `inbox/`
- Mode is always `consult_only`
- `allow_execute` is always `false`
- `allow_upload_files` is always `false`
- `reply_to` is set to the Telegram message ID

**Response:**
```
✅ Task created

🆔 ID: `a1b2c3d4e5f67890`
📌 Status: pending

💬 Prompt: 分析这个开源项目的架构并给出改进建议

🖥️ Next step: run this in your terminal:
```
cgpt-worker-once --mock
```

📖 Query result: /cgpt result a1b2c3d4e5f67890
```

---

## `/cgpt status`

Show queue status.

**Example:**
```
/cgpt status
```

**Response:**
```
📊 Queue Status

• Inbox (pending): 3
• Active: 0
• Outbox (completed): 12
• Failed: 0

📎 Recent tasks:
  - `a1b2c3d4e5f67890`
  - `b2c3d4e5f67890a1`
  - `c3d4e5f67890a1b2`
```

---

## `/cgpt result <task_id>`

Show result and report for a completed task.

**Example:**
```
/cgpt result a1b2c3d4e5f67890
```

**Response (completed):**
```
📄 Result for `a1b2c3d4e5f67890`

✅ Status: success
🔌 Adapter: mock

📝 Summary:
VISIBLE_CHATGPT_BRIDGE_OK

📁 Report: `/home/user/.openclaw/workspace/chatgpt-visible-bridge/reports/a1b2c3d4e5f67890.md`
```

**Response (pending):**
```
⏳ Task `a1b2c3d4e5f67890` is still pending.

Run this in your terminal to process:
```
cgpt-worker-once --mock
```
```

**Response (not found):**
```
🔍 Task `nonexistent123` not found.

Check status with /cgpt status
Or check the task ID is correct.
```

---

## `/cgpt show <task_id>`

Show task details and original prompt.

**Example:**
```
/cgpt show a1b2c3d4e5f67890
```

**Response:**
```
🔍 Task `a1b2c3d4e5f67890`

📌 Status: completed
🎯 Mode: consult_only
📅 Created: 2026-06-08T10:00:00+00:00
🔒 Policy: consult_only=True, execute=False, upload=False

💬 Prompt:
```
分析这个开源项目的架构并给出改进建议
```
```

---

## `/cgpt help`

Show usage help.

**Response:**
```
🤖 ChatGPT Visible Bridge — Telegram Commands

📌 Usage:

`/cgpt ask <prompt>` — Create a new task
  Example: `/cgpt ask Review the architecture of this project`

`/cgpt status` — Show queue status

`/cgpt result <task_id>` — Show result and report
  Example: `/cgpt result a1b2c3d4`

`/cgpt show <task_id>` — Show task details and prompt
  Example: `/cgpt show a1b2c3d4`

`/cgpt help` — Show this message

⚠️ All tasks are consult-only by default.
No automatic execution.
```

---

## `/agent approve <task_id>` (NOT IMPLEMENTED)

Approve execution of a task. **Not available in MVP or CGW-2.**

When implemented (future version), this would:
1. Check the task exists and has `policy.allow_execute=true`
2. Require explicit user confirmation
3. Flag the task as approved for execution
4. Wait for the next worker run to execute the suggested commands

---

## Notes

- All commands are **consult-only** by default.
- No command automatically executes local operations.
- The router only reads/writes local files; it does not run shell commands or scripts.
- Telegram is a **command entry layer**, not the core engine.
- Hermes / OpenClaw can route `/cgpt` commands to this module without including tokens in the repo.
- See [examples/hermes-router-example.py](hermes-router-example.py) for a generic integration example.
