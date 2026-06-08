# Release Notes v0.1.0

## What's New

This is the first public release of **ChatGPT Visible Bridge** (CGW), a manual, auditable, one-shot bridge between local agents and the ChatGPT Web interface.

## Core Features

- **File-based Task Queue**: JSON tasks in `inbox/`, processed one at a time, moved to `active/` then `outbox/` or `failed/`.
- **One-Shot Worker**: `cgpt-worker-once` processes exactly one task and exits. No daemon, no polling.
- **Mock Adapter (Default)**: Returns structured mock responses without touching the network. Safe for testing and validation.
- **Live Adapter Placeholder**: Returns `blocked` by default. Designed to connect to external browser bridges (e.g., codex-chatgpt-control) in future releases.
- **CLI Interface**: Six commands covering task creation, status check, worker execution, and result retrieval.
- **Human-Readable Reports**: Markdown reports generated for every task, with full prompt, response, and suggested next actions.

## Security Boundaries

- Consult-only by default. No automatic execution of ChatGPT-generated commands.
- No credential storage in the repository. `.env` is in `.gitignore`.
- No network calls in the MVP. Mock adapter is purely local.
- Live adapter is intentionally blocked. Real browser interaction requires a future bridge.
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

## Documentation

- `README.md` — Project overview and quick start
- `docs/ARCHITECTURE.md` — System design and data flow
- `docs/TASK_CONTRACT.md` — Task and Result JSON schemas
- `docs/TELEGRAM_WORKFLOW.md` — Telegram integration guide
- `docs/WORKER_MODES.md` — Worker modes and adapter behavior
- `docs/SECURITY_BOUNDARY.md` — Security and trust boundaries
- `docs/OPEN_SOURCE_RELEASE.md` — Release plan and roadmap
- `docs/PHASE_LOG.md` — Development phase log

## Known Limitations

- No real ChatGPT Web adapter (intentional for MVP).
- No Telegram bot wrapper (planned for v0.2.0).
- No execution mode (`policy.allow_execute` exists but is not implemented).
- No file upload support.
- No retry logic for failed tasks.
- No task templates or batch creation.

## Upgrade Notes

This is the initial release. No upgrade steps required.

## Compatibility

- Python >= 3.10
- No external dependencies (Python stdlib only)

## Contributors

chatgpt-visible-bridge contributors

## License

MIT
