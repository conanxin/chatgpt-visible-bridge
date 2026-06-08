# CGW-3A Live Adapter Skeleton

## Overview

CGW-3A introduces the **adapter-based worker architecture** for ChatGPT Visible Bridge. The worker can now be configured to use different adapters via the `--adapter` CLI flag.

```bash
cgpt-worker-once --adapter mock
cgpt-worker-once --adapter codex-chatgpt-control
```

**Important:** CGW-3A is a **skeleton phase**. The `codex-chatgpt-control` adapter returns `blocked` by default. It does **not** operate the real ChatGPT Web or call a real browser bridge.

## Adapter Architecture

```
chatgpt_visible_bridge/adapters/
├── __init__.py           # Public API exports
├── base.py               # Adapter ABC
├── mock.py               # MockAdapter (default, safe)
├── codex_chatgpt_control.py  # CodexChatGPTControlAdapter (skeleton)
└── registry.py           # get_adapter() factory + list_adapters()
```

### Adapter Interface

```python
class Adapter(ABC):
    name: str
    @property
    def available(self) -> bool: ...
    @abstractmethod
    def send(self, task: Task) -> Result: ...
```

### Adapter Registry

```python
from chatgpt_visible_bridge.adapters import get_adapter, list_adapters

get_adapter("mock")                    # -> MockAdapter
get_adapter("codex-chatgpt-control")    # -> CodexChatGPTControlAdapter
list_adapters()                        # -> ["mock", "codex-chatgpt-control"]
```

## Mock Adapter (Default)

The mock adapter remains the default and is unchanged from CGW-1/CGW-2.

```bash
cgpt-worker-once --mock              # backward compat
cgpt-worker-once --adapter mock      # explicit
```

Behavior:
- Returns structured mock responses
- No network calls
- Safe for testing and validation

## CodexChatGPTControlAdapter (CGW-3A Skeleton)

The skeleton adapter for the `codex-chatgpt-control` browser bridge.

```bash
cgpt-worker-once --adapter codex-chatgpt-control
```

### CGW-3A Behavior (Blocked by Default)

- **Does not call ChatGPT Web**
- **Does not call codex-chatgpt-control**
- **Does not launch a browser**
- Returns `blocked` status with:
  - `stop_reason: browser_bridge_unavailable`
  - `adapter: codex-chatgpt-control`
  - A detailed explanation in the summary

### Why Blocked?

A real browser bridge requires a **compatible host** with a live browser (e.g., Codex Desktop or a local Playwright bridge). This development environment does not have that capability.

### Dry-Run Mode (Optional)

If `CGW_LIVE_ADAPTER_DRY_RUN=1` is set, the adapter returns a dry-run blocked result with additional logging-style explanation.

```bash
CGW_LIVE_ADAPTER_DRY_RUN=1 cgpt-worker-once --adapter codex-chatgpt-control
```

### CGW-3B: Real Live Smoke (Future)

In CGW-3B, the adapter will:

1. Launch the browser bridge (e.g., `codex-chatgpt-control` CLI)
2. Send the wrapped prompt to the ChatGPT Web interface
3. Wait for the response
4. Return the actual ChatGPT response

**Requirements for CGW-3B:**
- Must run in a compatible browser bridge host (e.g., Codex Desktop)
- Must use manual one-shot mode (no background daemon)
- Must be visible and interruptible (headful browser, Ctrl+C to stop)
- Must report blockers (login required, captcha, rate limit)
- No file upload by default

## Blocked Result Handling

When a task is blocked by the adapter:

1. **Result JSON** is written to `outbox/<task_id>.json` with:
   - `status: "blocked"`
   - `stop_reason: "browser_bridge_unavailable"`
   - `adapter: "codex-chatgpt-control"`

2. **Report Markdown** is written to `reports/<task_id>.md` with:
   - Full blocker explanation
   - CGW-3A skeleton status
   - Next phase recommendation (CGW-3B)

3. **Task record** is moved to `failed/<task_id>.json` with:
   - `status: "blocked"`

4. **Telegram /cgpt result** displays the blocked status with the summary and a link to the report.

## CLI Support

| Command | Behavior |
|---------|----------|
| `cgpt-worker-once --mock` | Backward compat; uses mock adapter |
| `cgpt-worker-once --adapter mock` | Explicit mock adapter |
| `cgpt-worker-once --adapter codex-chatgpt-control` | Skeleton; returns blocked |
| `cgpt-worker-drain --adapter <name>` | Same options for drain mode |

## Backward Compatibility

The old `chatgpt_visible_bridge.adapter` module is preserved and re-exports from the new `chatgpt_visible_bridge.adapters` package.

```python
from chatgpt_visible_bridge.adapter import get_adapter  # still works
from chatgpt_visible_bridge.adapters import get_adapter  # preferred
```

The old `LiveAdapter` name is preserved as an alias for `CodexChatGPTControlAdapter`.

## Security

- **No real ChatGPT Web operation in CGW-3A.**
- **No browser launched.**
- **No network calls.**
- **No cookie/session/profile access.**
- **No file upload/download.**
- **No background daemon.**

See [docs/SECURITY_BOUNDARY.md](SECURITY_BOUNDARY.md) for full security boundaries.
