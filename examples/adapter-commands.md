# Adapter Commands Reference

## Mock Adapter (Default)

```bash
# Create a task
cgpt-create-task --prompt "Analyze this architecture"

# Process with mock adapter (default)
cgpt-worker-once --mock
cgpt-worker-once --adapter mock

# Expected result: success, structured mock response
```

## CodexChatGPTControlAdapter (CGW-3A Skeleton)

```bash
# Create a task
cgpt-create-task --prompt "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"

# Process with codex-chatgpt-control skeleton adapter
# This returns blocked because no real browser bridge is available
cgpt-worker-once --adapter codex-chatgpt-control

# Expected result:
#   Status: blocked
#   Adapter: codex-chatgpt-control
#   Stop Reason: browser_bridge_unavailable
#   Summary: CGW-3A Skeleton Status explanation
```

## Telegram Router Result for Blocked Task

```bash
# After worker-once with codex adapter, query result via Telegram router
cgpt-telegram-router "/cgpt result <task_id>"

# Expected output:
#   📄 Result for `<task_id>`
#   ✅ Status: blocked
#   🔌 Adapter: codex-chatgpt-control
#   📝 Summary: CGW-3A Skeleton Status...
#   📁 Report: /path/to/report.md
```

## CLI Worker Commands

| Command | Adapter | Behavior |
|---------|---------|----------|
| `worker-once --mock` | mock | Backward compat; processes with mock |
| `worker-once --adapter mock` | mock | Explicit mock adapter |
| `worker-once --adapter codex-chatgpt-control` | codex-chatgpt-control | Returns blocked (skeleton) |
| `worker-drain --adapter mock` | mock | Drain all with mock |
| `worker-drain --adapter codex-chatgpt-control` | codex-chatgpt-control | Drain all with blocked results |

## Notes

- **Mock adapter** is the default and safe for testing.
- **CodexChatGPTControlAdapter** is a skeleton in CGW-3A; it does not operate real ChatGPT Web.
- **CGW-3B** will implement real live smoke from a compatible browser bridge host.
- All tasks are consult-only by default.
- No file upload or download in CGW-3A.
