# ChatGPT Visible Bridge

A manual, auditable, open-source bridge between local agents and the ChatGPT Web interface.

> **Not an API wrapper. Not a headless bot. This is a task queue with a one-shot worker.**

## What This Is

`chatgpt-visible-bridge` (CGW) is a glue layer that lets you:

1. **Create tasks** from Telegram, CLI, or your local agent — by writing a JSON file to an `inbox/` directory.
2. **Manually run** a one-shot worker when you're ready — it reads the task, sends a prepared prompt to ChatGPT (via mock adapter or a future browser bridge), and writes the result to `outbox/` and `reports/`.
3. **Review and approve** — results are consult-only by default. The next action is a suggestion, never an auto-execution.

## What This Is NOT

- ❌ **OpenAI API wrapper** — This does not use `api.openai.com`. It targets the ChatGPT Web interface.
- ❌ **Unattended browser bot** — The worker is manual, one-shot, and opt-in. No watch daemon by default.
- ❌ **Auto-executor** — `/cgpt` commands are **consult-only**. Real execution requires explicit `/agent approve` and is not implemented in the MVP.
- ❌ **Telegram bot** — Telegram is an optional notification/query channel, not the core engine.

## Architecture (MVP)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Telegram   │     │   Inbox      │     │   One-Shot   │     │   Outbox/    │
│   / CLI      │────▶│   Task JSON  │────▶│   Worker     │────▶│   Reports    │
│   (cgpt)     │     │   (pending)  │     │   (manual)   │     │   (completed)│
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │  Mock Adapter│  (default)
                                         │  or          │
                                         │  Live Adapter│  (future)
                                         └──────────────┘
```

## Default Mode: Mock Adapter

The first release ships with a **MockAdapter** that returns structured mock responses. This lets you:
- Test the full pipeline without touching ChatGPT Web.
- Validate the task contract and report format.
- Build the workflow before connecting a real browser bridge.

## Live Adapter (Future)

A placeholder `LiveAdapter` exists but returns `blocked` by default. To connect to the real ChatGPT Web, you will need an external browser bridge (e.g., `codex-chatgpt-control` or a Codex/Playwright bridge). This is explicitly out of scope for the MVP.

## Quick Start

```bash
# 1. Clone
git clone https://github.com/<user>/chatgpt-visible-bridge.git
cd chatgpt-visible-bridge

# 2. Install (Python 3.10+)
pip install -e .

# 3. Create a task
cgpt-create-task --prompt "Analyze the feasibility of rewriting this project in Rust"

# 4. Check status
cgpt-task-status

# 5. Run the one-shot worker
cgpt-worker-once --mock

# 6. View the result
cgpt-task-result <task_id>
```

## Directory Layout (Runtime)

Default workspace: `~/.openclaw/workspace/chatgpt-visible-bridge/`

```
chatgpt-visible-bridge/
├── inbox/      # Pending tasks (JSON)
├── active/     # Task currently being processed
├── outbox/     # Completed results (JSON)
├── failed/     # Failed or blocked tasks (JSON)
├── reports/    # Human-readable markdown reports
└── logs/       # Worker execution logs
```

Override with `CGW_HOME` environment variable.

## Task JSON Schema

See [docs/TASK_CONTRACT.md](docs/TASK_CONTRACT.md) and [examples/task.example.json](examples/task.example.json).

## CLI Commands

| Command | Purpose |
|---------|---------|
| `cgpt-create-task` | Create a task in inbox |
| `cgpt-task-status` | Show queue summary |
| `cgpt-worker-once` | Process one task, then exit |
| `cgpt-worker-drain` | Process all pending tasks, then exit |
| `cgpt-task-result` | Show result and report |
| `cgpt-task-show` | Show raw prompt and task detail |

## Modes & Policies

- **consult-only (default)**: ChatGPT-generated suggestions are saved as recommendations. No local execution.
- **execute (not in MVP)**: Requires `policy.allow_execute=true` and explicit user approval. Not implemented yet.
- **upload (not in MVP)**: Requires `policy.allow_upload_files=true`. Not implemented yet.

## Security Boundaries

- No automatic execution of local commands.
- No unattended browser sessions.
- No credential storage (no tokens, no cookies, no session data in the repo).
- No Telegram bot token in the repository.
- Task files are local-only. No network calls in the MVP.

See [docs/SECURITY_BOUNDARY.md](docs/SECURITY_BOUNDARY.md) for details.

## Open Source

- **License**: MIT
- **Status**: MVP — looking for feedback before v1.0

See [docs/OPEN_SOURCE_RELEASE.md](docs/OPEN_SOURCE_RELEASE.md) for the release plan and roadmap.

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — System design and data flow
- [docs/TASK_CONTRACT.md](docs/TASK_CONTRACT.md) — Task JSON schema and lifecycle
- [docs/TELEGRAM_WORKFLOW.md](docs/TELEGRAM_WORKFLOW.md) — Telegram integration guide
- [docs/WORKER_MODES.md](docs/WORKER_MODES.md) — Worker modes and adapter behavior
- [docs/SECURITY_BOUNDARY.md](docs/SECURITY_BOUNDARY.md) — Security and trust boundaries
- [docs/OPEN_SOURCE_RELEASE.md](docs/OPEN_SOURCE_RELEASE.md) — Release plan and roadmap
- [docs/PHASE_LOG.md](docs/PHASE_LOG.md) — Development phase log

## Contributing

Issues and PRs welcome. Please keep the MVP minimal — this is a glue layer, not an automation framework.
