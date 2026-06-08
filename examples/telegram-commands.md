# Telegram Commands Reference

## `/cgpt <prompt>`

Create a consult-only task from Telegram.

**Example:**
```
/cgpt 分析这个开源项目的架构并给出改进建议
```

**Behavior:**
- Creates a task JSON in `inbox/`
- Mode is always `consult_only`
- `reply_to` is set to the Telegram message ID

**Response:**
```
✅ Task created: a1b2c3d4e5f67890
   Status: pending
   Run `cgpt-worker-once --mock` to process.
```

---

## `/cgpt_status`

Show queue status.

**Example:**
```
/cgpt_status
```

**Response:**
```
📊 Queue Status
  Inbox (pending):   3
  Active:            0
  Outbox (completed): 12
  Failed:            0
```

---

## `/cgpt_result <task_id>`

Show result and report for a completed task.

**Example:**
```
/cgpt_result a1b2c3d4e5f67890
```

**Response:**
```
📄 Result for a1b2c3d4e5f67890
Status: success
Adapter: mock

## 任务理解
...

Report: /home/conanxin/.openclaw/workspace/chatgpt-visible-bridge/reports/a1b2c3d4e5f67890.md
```

---

## `/agent approve <task_id>` (NOT IMPLEMENTED)

Approve execution of a task. **Not available in MVP.**

When implemented (v0.4.0+), this would:
1. Check the task exists and has `policy.allow_execute=true`
2. Flag the task as approved for execution
3. Wait for the next worker run to execute the suggested commands

---

## Notes

- All commands are **consult-only** by default.
- No command automatically executes local operations.
- The bot only reads/writes local files; it does not run shell commands.
