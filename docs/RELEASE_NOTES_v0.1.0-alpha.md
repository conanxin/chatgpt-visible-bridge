# Release Notes v0.1.0-alpha

## What's New

This is the first alpha release of **ChatGPT Visible Bridge** (CGW), a manual, auditable, one-shot bridge between local agents and the ChatGPT Web interface.

**Status:** Alpha — looking for feedback and real-world testing. Live ChatGPT Web smoke requires a compatible browser bridge host (e.g., Codex Desktop) and is not confirmed in all environments.

## What Works Now

### Core Pipeline
- **File-based Task Queue**: JSON tasks in `inbox/`, processed one at a time, moved to `active/` then `outbox/` or `failed/`.
- **One-Shot Worker**: `cgpt-worker-once` processes exactly one task and exits. No daemon, no polling.
- **Mock Adapter (Default)**: Returns structured mock responses without touching the network. Safe for testing and validation.
- **CLI Interface**: Seven commands covering task creation, status check, worker execution, result retrieval, and Telegram simulation.
- **Human-Readable Reports**: Markdown reports generated for every task, with full prompt, response, and suggested next actions.

### Telegram / Hermes Router
- **Command Router**: `/cgpt ask`, `/cgpt status`, `/cgpt result`, `/cgpt show`, `/cgpt help`
- **Consult-only by default**: All tasks created with `allow_execute=false`, `allow_upload=false`
- **CLI Simulation**: `cgpt-telegram-router` for developer testing without a real Telegram bot
- **Hermes Integration**: Example showing how OpenClaw/Hermes can intercept `/cgpt` commands

### Live Adapter (Guarded Experimental)
- **Adapter Registry**: `mock` and `codex-chatgpt-control` adapters
- **Guarded Path**: `--live` flag and `CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1` required for real live smoke
- **Safe Defaults**: Without explicit live enablement, returns `blocked` with `stop_reason: live_not_enabled`
- **Blocker Reports**: Structured reporting for `dependency_missing`, `browser_bridge_unavailable`
- **No Hidden Automation**: No file upload, no credential reading, no command execution

## What Does Not Work Yet

- **No confirmed real visible ChatGPT Web live smoke in all environments** — requires compatible browser bridge host (e.g., Codex Desktop with ChatGPT Web already logged in)
- **No file upload/download** — not implemented
- **No automatic local agent execution** — consult-only by design
- **No default watch daemon** — one-shot by design
- **No Telegram bot implementation** — router is a library, requires a real bot or gateway for production

## Security Boundaries

- Consult-only by default. No automatic execution of ChatGPT-generated commands.
- No credential storage in the repository. `.env` is in `.gitignore`.
- No network calls in the mock path. Mock adapter is purely local.
- Live adapter is intentionally guarded. Real browser interaction requires explicit flags and a compatible host.
- Worker is one-shot, not a daemon. User must explicitly trigger every run.

## CLI Commands

| Command | Description |
|---------|-------------|
| `cgpt-create-task` | Create a task in inbox |
| `cgpt-task-status` | Show queue summary |
| `cgpt-worker-once` | Process one task, then exit |
| `cgpt-worker-drain` | Process all pending tasks, then exit |
| `cgpt-task-result` | Show result JSON and report |
| `cgpt-task-show` | Show raw and wrapped prompt |
| `cgpt-telegram-router` | Simulate Telegram message (developer helper) |

### Adapter Options

```bash
# Mock adapter (default)
cgpt-worker-once --mock
cgpt-worker-once --adapter mock

# CodexChatGPTControlAdapter (guarded experimental)
cgpt-worker-once --adapter codex-chatgpt-control

# Explicit live smoke (requires compatible browser bridge host)
CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1 cgpt-worker-once --adapter codex-chatgpt-control --live
```

## Documentation

- `README.md` — Project overview and quick start
- `docs/ARCHITECTURE.md` — System design and data flow
- `docs/TASK_CONTRACT.md` — Task and Result JSON schemas
- `docs/TELEGRAM_WORKFLOW.md` — Telegram integration guide
- `docs/WORKER_MODES.md` — Worker modes and adapter behavior
- `docs/SECURITY_BOUNDARY.md` — Security and trust boundaries
- `docs/OPEN_SOURCE_RELEASE.md` — Release plan and roadmap
- `docs/PHASE_LOG.md` — Development phase log
- `docs/CGW2_TELEGRAM_ROUTER.md` — Telegram router architecture
- `docs/HERMES_INTEGRATION.md` — Hermes / OpenClaw integration guide
- `docs/CGW3A_LIVE_ADAPTER_SKELETON.md` — Live adapter skeleton
- `docs/CGW3B_LIVE_SMOKE.md` — Guarded live smoke requirements
- `docs/CGW3C_LIVE_ENV_PREFLIGHT.md` — Live environment preflight

## Tests

75 tests passing. Run with:
```bash
python3 -m pytest tests/ -v
```

## Compatibility

- Python >= 3.10
- No external dependencies (Python stdlib only)

## Contributors

chatgpt-visible-bridge contributors

## License

MIT
