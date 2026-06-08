# Changelog

## v0.1.0-alpha (2026-06-08)

### CGW-1: Task Queue, CLI, and Mock Worker
- File-based task queue (`inbox/`, `active/`, `outbox/`, `failed/`, `reports/`)
- Task and Result JSON schema with policy support
- MockAdapter (default) with structured responses
- One-shot worker (`cgpt-worker-once`, `cgpt-worker-drain`)
- CLI commands: create-task, task-status, worker-once, worker-drain, task-result, task-show
- 24 tests passing

### CGW-2: Telegram / Hermes Router MVP
- Telegram command parser (`/cgpt ask`, `/cgpt status`, `/cgpt result`, `/cgpt show`, `/cgpt help`)
- TelegramHandler connecting commands to task queue
- Telegram-friendly formatting (emoji, bullet lists)
- CLI simulation command (`cgpt-telegram-router`)
- Hermes / OpenClaw integration example
- 28 new tests (52 total)

### CGW-3A: Live Adapter Skeleton
- Adapter-based architecture (`chatgpt_visible_bridge/adapters/`)
- `CodexChatGPTControlAdapter` skeleton returning `blocked` by default
- `get_adapter()` factory with registry
- Backward compatibility preserved
- 17 new tests (69 total)

### CGW-3B: Guarded Live Smoke Path
- Guarded live path: `--live` flag and `CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1` required
- Live preflight checks: dependency check, browser bridge availability
- Structured blocker reports (`live_not_enabled`, `dependency_missing`, `browser_bridge_unavailable`)
- 6 new tests (75 total)

### CGW-3C: Live Environment Preflight
- Documented live environment requirements and blockers
- WSL/Hermes runtime confirmed as NO-GO for live smoke
- Safe default behavior maintained

### Known Limitations (v0.1.0-alpha)
- No confirmed real visible ChatGPT Web live smoke in current WSL/Hermes runtime
- No file upload/download
- No automatic local agent execution
- No default watch daemon
- Live adapter requires compatible browser bridge host (e.g., Codex Desktop)

## Future Roadmap

- **CGW-3D**: Real live smoke from compatible browser bridge host
- **CGW-4B**: GitHub Release automation
- **CGW-5**: Full Telegram → manual live worker → Telegram result flow
- **v1.0**: Stable API with community feedback
