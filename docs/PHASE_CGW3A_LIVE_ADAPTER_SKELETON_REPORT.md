# Phase CGW-3A Live Adapter Skeleton Report

## 1. Goal

Add an **adapter-based worker architecture** to ChatGPT Visible Bridge, introducing the `codex-chatgpt-control` adapter skeleton while keeping the mock adapter as the default.

Key constraints:
- CGW-3A is **skeleton-only** — no real ChatGPT Web operation.
- The `codex-chatgpt-control` adapter returns `blocked` by default (`browser_bridge_unavailable`).
- All existing tests and CLI behavior must be preserved.
- CGW-3B will implement real live smoke from a compatible browser bridge host.

## 2. Why CGW-3A is Skeleton/Blocker-Safe Only

Before attempting real browser automation, we must:
1. **Ensure the adapter interface is clean** — pluggable, testable, well-documented.
2. **Ensure blocked paths are safe** — if the browser bridge is missing, the worker must return a clear `blocked` result, not crash or hang.
3. **Ensure Telegram users can understand the blocker** — the `/cgpt result` output must clearly say "blocked" and explain why.
4. **Ensure no accidental real Web operation** — the skeleton must be explicitly blocked by default, requiring CGW-3B to enable real behavior.

## 3. Files Added / Changed

### Added (6 files)

| File | Description |
|------|-------------|
| `chatgpt_visible_bridge/adapters/__init__.py` | Public API exports |
| `chatgpt_visible_bridge/adapters/base.py` | Adapter ABC (`send`, `available`) |
| `chatgpt_visible_bridge/adapters/mock.py` | MockAdapter (default, unchanged behavior) |
| `chatgpt_visible_bridge/adapters/codex_chatgpt_control.py` | CodexChatGPTControlAdapter skeleton (blocked by default) |
| `chatgpt_visible_bridge/adapters/registry.py` | `get_adapter()` factory + `list_adapters()` |
| `examples/adapter-commands.md` | Adapter command reference |
| `docs/CGW3A_LIVE_ADAPTER_SKELETON.md` | Adapter architecture and CGW-3A behavior docs |
| `tests/test_adapters.py` | 11 adapter unit tests |
| `tests/test_cgw3a_blocked.py` | 6 integration tests for blocked behavior |

### Modified (6 files)

| File | Change |
|------|--------|
| `chatgpt_visible_bridge/adapter.py` | Re-exports from new `adapters/` package; backward-compatible `LiveAdapter` alias |
| `chatgpt_visible_bridge/cli.py` | Updated `--adapter` help text to mention `codex-chatgpt-control` |
| `README.md` | Added Live Adapter Skeleton section, adapter CLI options, docs link |
| `docs/ARCHITECTURE.md` | Updated Adapter layer section for CGW-3A |
| `docs/WORKER_MODES.md` | Added Adapter selection table and live mode details |
| `docs/SECURITY_BOUNDARY.md` | Added Live Adapter security constraints section |
| `docs/PHASE_LOG.md` | Added CGW-3A development log |

## 4. Adapter Architecture

```
chatgpt_visible_bridge/adapters/
├── base.py                    # Adapter ABC
├── mock.py                    # MockAdapter (default)
├── codex_chatgpt_control.py   # CodexChatGPTControlAdapter (skeleton)
└── registry.py                # get_adapter(), list_adapters()
```

### Registry

```python
from chatgpt_visible_bridge.adapters import get_adapter, list_adapters

get_adapter("mock")                    # -> MockAdapter
get_adapter("codex-chatgpt-control")    # -> CodexChatGPTControlAdapter
list_adapters()                        # -> ["mock", "codex-chatgpt-control"]
```

### Backward Compatibility

```python
from chatgpt_visible_bridge.adapter import get_adapter  # still works
from chatgpt_visible_bridge.adapters import get_adapter   # preferred
```

## 5. CLI Behavior

### Mock Adapter (Default)

```bash
# Backward compatible
cgpt-worker-once --mock

# Explicit
cgpt-worker-once --adapter mock
```

- Returns `success` status
- Returns structured mock response
- No network calls
- VISIBLE_CHATGPT_BRIDGE_OK smoke test passes

### CodexChatGPTControlAdapter (Skeleton)

```bash
cgpt-worker-once --adapter codex-chatgpt-control
```

- Returns `blocked` status
- `stop_reason: browser_bridge_unavailable`
- `adapter: codex-chatgpt-control`
- Detailed summary explaining CGW-3A skeleton status
- Suggested next action: "Run CGW-3B from a compatible browser bridge host"
- No real ChatGPT Web operation attempted
- No browser launched
- No network calls

## 6. Blocked Result Behavior

When processing with `codex-chatgpt-control` adapter:

1. **Result JSON** (`outbox/<task_id>.json`):
   ```json
   {
     "id": "...",
     "status": "blocked",
     "summary": "## CGW-3A Skeleton Status\n\n...",
     "adapter": "codex-chatgpt-control",
     "stop_reason": "browser_bridge_unavailable",
     "suggested_next_action": "Run CGW-3B from a compatible browser bridge host..."
   }
   ```

2. **Report Markdown** (`reports/<task_id>.md`):
   - Full blocker explanation
   - CGW-3A skeleton status
   - Next phase recommendation (CGW-3B)

3. **Task record** moved to `failed/<task_id>.json` with `status: "blocked"`

## 7. Telegram Result Behavior

`/cgpt result <task_id>` for a blocked task displays:

```
📄 Result for `<task_id>`

✅ Status: blocked
🔌 Adapter: codex-chatgpt-control

📝 Summary:
## CGW-3A Skeleton Status

This is the `codex-chatgpt-control` adapter skeleton.

**No real ChatGPT Web operation was attempted.**
...

📁 Report: `/path/to/report.md`
```

The blocked status is clearly visible, and the summary explains why.

## 8. Tests

```bash
PYTHONPATH=/home/conanxin/chatgpt-visible-bridge python3 -m pytest tests/ -v
============================== 69 passed in 0.28s
```

| Test File | Count | Coverage |
|-----------|-------|----------|
| `test_adapters.py` | 11 | Registry, mock, codex, backward compat, dry-run |
| `test_cgw3a_blocked.py` | 6 | Worker blocked, report content, Telegram display, CLI, status |
| Existing tests (CGW-1/2) | 52 | All still pass |

### Specific CGW-3A Tests

- `test_adapter_registry_includes_mock` ✅
- `test_adapter_registry_includes_codex_chatgpt_control` ✅
- `test_codex_adapter_returns_blocked` ✅
- `test_codex_adapter_not_available` ✅
- `test_codex_adapter_dry_run` ✅
- `test_worker_with_codex_adapter_blocked` ✅
- `test_blocked_result_has_report_path` ✅
- `test_telegram_router_blocked_result` ✅
- `test_blocked_report_content` ✅
- `test_blocked_task_status_in_workspace` ✅
- `test_cli_worker_once_with_codex_adapter` ✅

## 9. Smoke Results

### Smoke 1: Mock Adapter

```bash
export CGW_HOME=/tmp/cgw3a-mock
rm -rf /tmp/cgw3a-mock

python3 -m chatgpt_visible_bridge.cli create-task --prompt "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"
python3 -m chatgpt_visible_bridge.cli worker-once --adapter mock
python3 -m chatgpt_visible_bridge.cli task-status
```

Result:
- Task created: b116c965b5c14134
- Status: success
- Report contains: VISIBLE_CHATGPT_BRIDGE_OK ✅

### Smoke 2: CodexChatGPTControl Skeleton Blocked

```bash
export CGW_HOME=/tmp/cgw3a-live-skeleton
rm -rf /tmp/cgw3a-live-skeleton

python3 -m chatgpt_visible_bridge.cli create-task --prompt "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"
python3 -m chatgpt_visible_bridge.cli worker-once --adapter codex-chatgpt-control
python3 -m chatgpt_visible_bridge.cli task-status
```

Result:
- Task created: 491fb7502ff246f6
- Status: blocked ✅
- Adapter: codex-chatgpt-control ✅
- Stop reason: browser_bridge_unavailable ✅
- Report contains: "CGW-3A Skeleton Status", "No real ChatGPT Web operation" ✅
- Result JSON: status=blocked, adapter=codex-chatgpt-control ✅
- Task moved to failed/ with BLOCKED status ✅

### Smoke 3: Telegram Router Blocked Result

```bash
export CGW_HOME=/tmp/cgw3a-live-skeleton
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt result 491fb7502ff246f6"
```

Result:
- Output contains: "blocked" ✅
- Output contains: "codex-chatgpt-control" ✅
- Output contains: "CGW-3B" / "browser bridge" ✅
- Output contains full summary and report path ✅

## 10. Security / Open-Source Check

| Check | Method | Result |
|-------|--------|--------|
| TELEGRAM token patterns | `grep -rni "bot_token\|TELEGRAM_BOT_TOKEN"` | No matches in code (only CLI command names like task-result) |
| OpenAI key patterns | `grep -rni "openai.*key\|sk-"` | No matches |
| Cookie/session strings | `grep -rni "cookie\|session_id"` | No matches in code |
| chat_id hardcoding | `grep -rni "1540208324\|chat_id.*=[0-9]"` | No matches |
| Browser profile paths | `grep -rni "chrome.*profile\|user_data_dir"` | No matches |
| `.env` committed | `git ls-files | grep .env` | No `.env` files in git |
| `.env.example` generic | Manual inspection | ✅ Placeholder values only |

### Conclusion

- ✅ No real token, session, cookie, or chat_id hardcoded
- ✅ No browser profile or cookie paths referenced
- ✅ No real ChatGPT Web operation attempted in CGW-3A
- ✅ `.env` not committed; `.env.example` is generic
- ✅ All examples are open-source safe

## 11. Git Status Before Commit

```
Changes not staged:
  modified:   README.md
  modified:   chatgpt_visible_bridge/adapter.py
  modified:   chatgpt_visible_bridge/cli.py
  modified:   docs/ARCHITECTURE.md
  modified:   docs/PHASE_LOG.md
  modified:   docs/SECURITY_BOUNDARY.md
  modified:   docs/WORKER_MODES.md
Untracked files:
  chatgpt_visible_bridge/adapters/
  docs/CGW3A_LIVE_ADAPTER_SKELETON.md
  examples/adapter-commands.md
  tests/test_adapters.py
  tests/test_cgw3a_blocked.py
```

## 12. Commit Hash After Commit

```
a6e79aa docs: update CGW-3A report with final commit hash
bc4e294 Add live adapter skeleton for ChatGPT visible bridge
```

## 13. Remaining Limitations

| Limitation | Reason | Future Phase |
|------------|--------|--------------|
| No real ChatGPT Web adapter | CGW-3A is skeleton-only | CGW-3B: real live smoke |
| No real browser automation | Blocked by default | CGW-3B: codex-chatgpt-control integration |
| No file upload/download | Not in scope | Future with explicit selection |
| No execution mode | Consult-only by design | Future with `/agent approve` |
| No watch mode | One-shot by design | Future optional daemon |

## 14. Next Phase CGW-3B Recommendation

**Goal:** Implement real live smoke from a compatible browser bridge host.

### Requirements

1. **Run in compatible browser bridge host** (e.g., Codex Desktop or local Playwright bridge)
2. **Manual one-shot only** — `cgpt-worker-once --adapter codex-chatgpt-control`
3. **No file upload** — keep `allow_upload_files=false` as default
4. **Blocker reporting** — if the bridge encounters issues:
   - Return `ResultStatus.BLOCKED`
   - Set `stop_reason` to descriptive blocker (`login_required`, `captcha`, `rate_limited`)
   - Write a report explaining the blocker
5. **Visible and interruptible** — headful browser, Ctrl+C to stop, hard timeout (5 min)

### Suggested Smoke Test for CGW-3B

```bash
# From a compatible browser bridge host (e.g., Codex Desktop)
export CGW_HOME=/tmp/cgw3b-live
rm -rf /tmp/cgw3b-live

# Create task
python3 -m chatgpt_visible_bridge.cli create-task \
  --prompt "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"

# Run with real live adapter
python3 -m chatgpt_visible_bridge.cli worker-once \
  --adapter codex-chatgpt-control

# Verify result
python3 -m chatgpt_visible_bridge.cli task-result <task_id>
```

**Expected result:** `status: success`, `summary: VISIBLE_CHATGPT_BRIDGE_OK`, `adapter: codex-chatgpt-control`

## 15. Go / No-Go Judgment

### Acceptance Criteria Check

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Adapter registry supports mock and codex-chatgpt-control | ✅ | `test_adapter_registry_includes_*` + `list_adapters()` |
| 2 | `--adapter mock` works and preserves VISIBLE_CHATGPT_BRIDGE_OK | ✅ | Smoke 1 + existing tests |
| 3 | `--mock` backward compatibility works | ✅ | `test_cli_worker_once_mock` |
| 4 | `--adapter codex-chatgpt-control` returns blocked/browser_bridge_unavailable, not crash | ✅ | Smoke 2 + `test_worker_with_codex_adapter_blocked` |
| 5 | Blocked result writes report and result JSON | ✅ | `test_blocked_result_has_report_path` + Smoke 2 |
| 6 | `/cgpt result` can display blocked result | ✅ | Smoke 3 + `test_telegram_router_blocked_result` |
| 7 | All tests pass | ✅ | 69/69 passed in 0.28s |
| 8 | Docs updated | ✅ | CGW3A_LIVE_ADAPTER_SKELETON, ARCHITECTURE, WORKER_MODES, SECURITY_BOUNDARY, README, PHASE_LOG |
| 9 | Examples updated | ✅ | `examples/adapter-commands.md` |
| 10 | No real token/cookie/session/chat_id/browser profile hardcoding | ✅ | Security scan |
| 11 | No real ChatGPT Web operation attempted | ✅ | Skeleton returns blocked by default |
| 12 | Local git commit created | ✅ | `6928601` + `39e1b1b` |
| 13 | Final report exists | ✅ | This file: `docs/PHASE_CGW3A_LIVE_ADAPTER_SKELETON_REPORT.md` |

### Judgment

🟢 **GO**

All 13 acceptance criteria are met. The adapter skeleton is safe, well-tested, and ready for CGW-3B real live smoke implementation.

---

*Report generated: 2026-06-08*
*CGW-3A version: v0.3.0-dev*
*Total tests: 69/69 passing*
