# ChatGPT Visible Bridge

A manual, auditable, open-source bridge between local agents and the ChatGPT Web interface. **v0.1.0-alpha** — Alpha release.

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

## Live Adapter (CGW-3B Guarded Smoke)

A `CodexChatGPTControlAdapter` is available for guarded live smoke through `codex-chatgpt-control`.
It remains blocked by default unless live mode is explicitly enabled.

```bash
# Safe default: no real ChatGPT Web operation
cgpt-worker-once --adapter codex-chatgpt-control

# Explicit one-shot live smoke from a compatible Codex/browser bridge host
export CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1
cgpt-worker-once --adapter codex-chatgpt-control --live
```

**CGW-3B behavior:**
- Without `--live` or `CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1`, returns `blocked` with `stop_reason: live_not_enabled`
- If the package is unavailable, returns `blocked` with `stop_reason: dependency_missing`
- If the browser bridge is unavailable, returns `blocked` with `stop_reason: browser_bridge_unavailable`
- On success, writes `response_markdown` to `outbox/` and a human-readable report to `reports/`
- Does not upload files, download files, read cookies/session data, or execute ChatGPT returned commands

Ordinary shell execution is expected to block safely. Real live smoke requires a compatible Codex/browser bridge host with ChatGPT Web already logged in. See [docs/CGW3B_LIVE_SMOKE.md](docs/CGW3B_LIVE_SMOKE.md).

## Telegram / Hermes Router MVP

The project now includes a **Telegram command router** (`chatgpt_visible_bridge.telegram`) that lets you interact with the task queue via Telegram-style commands without touching the real Telegram API.

### Supported Telegram Commands

| Command | Description | Policy |
|---------|-------------|--------|
| `/cgpt ask <prompt>` | Create a consult-only task | `allow_execute=false`, `allow_upload=false` |
| `/cgpt status` | Show queue status | Read-only |
| `/cgpt result <task_id>` | Show result and report | Read-only |
| `/cgpt show <task_id>` | Show task details and prompt | Read-only |
| `/cgpt help` | Show usage instructions | Read-only |

### How It Works

1. **Telegram is only a command entry** — the router parses `/cgpt` text into local file operations.
2. **Hermes / OpenClaw can route** `/cgpt` commands to the `chatgpt_visible_bridge` module without including tokens in this repo.
3. **All `/cgpt` commands are consult-only** — tasks are created with `consult_only=true`, `allow_execute=false`.
4. **ChatGPT-generated commands are not executed automatically** — the router only creates/reads files; execution requires manual `cgpt-worker-once`.
5. **`/agent approve` is future work** — not implemented in CGW-2. It will require explicit user confirmation when added.
6. **CGW-2 does not use the real Telegram API** — the router is a library; a real bot or gateway is required for production.
7. **CGW-2 does not operate the real ChatGPT Web** — mock adapter is still the default.

### Developer Testing (CLI Simulation)

```bash
# Simulate a Telegram message without a real bot
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt ask Review the architecture"

# Check status
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt status"

# Run the worker
python3 -m chatgpt_visible_bridge.cli worker-once --mock

# Get the result
python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt result <task_id>"
```

See [docs/HERMES_INTEGRATION.md](docs/HERMES_INTEGRATION.md) for how to wire this into Hermes/OpenClaw.

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
| `cgpt-telegram-router` | Simulate Telegram message (developer helper) |

### Adapter Options

```bash
# Mock adapter (default)
cgpt-worker-once --mock
cgpt-worker-once --adapter mock

# CodexChatGPTControlAdapter skeleton (CGW-3A)
cgpt-worker-once --adapter codex-chatgpt-control

# Guarded live smoke (CGW-3B)
CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1 cgpt-worker-once --adapter codex-chatgpt-control --live
```

## Modes & Policies

- **consult-only (default)**: ChatGPT-generated suggestions are saved as recommendations. No local execution.
- **execute (not in MVP)**: Requires `policy.allow_execute=true` and explicit user approval. Not implemented yet.
- **upload (not in MVP)**: Requires `policy.allow_upload_files=true`. Not implemented yet.

## Security Boundaries

- No automatic execution of local commands.
- No unattended browser sessions.
- No credential storage (no tokens, no cookies, no session data in the repo).
- No Telegram bot token in the repository.
- Live adapter is explicit, one-shot, and blocker-safe.
- Task files are local-only unless the user explicitly runs guarded live smoke.

See [docs/SECURITY_BOUNDARY.md](docs/SECURITY_BOUNDARY.md) for details.

## Open Source

- **License**: MIT
- **Status**: v0.1.0-alpha — Alpha release
- **Roadmap**: [ROADMAP.md](ROADMAP.md)
- **Latest Release**: [v0.1.0-alpha](https://github.com/conanxin/chatgpt-visible-bridge/releases/tag/v0.1.0-alpha)

See [docs/OPEN_SOURCE_RELEASE.md](docs/OPEN_SOURCE_RELEASE.md) for the release plan and roadmap.

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — System design and data flow
- [docs/TASK_CONTRACT.md](docs/TASK_CONTRACT.md) — Task JSON schema and lifecycle
- [docs/TELEGRAM_WORKFLOW.md](docs/TELEGRAM_WORKFLOW.md) — Telegram integration guide
- [docs/WORKER_MODES.md](docs/WORKER_MODES.md) — Worker modes and adapter behavior
- [docs/SECURITY_BOUNDARY.md](docs/SECURITY_BOUNDARY.md) — Security and trust boundaries
- [docs/OPEN_SOURCE_RELEASE.md](docs/OPEN_SOURCE_RELEASE.md) — Release plan and roadmap
- [docs/PHASE_LOG.md](docs/PHASE_LOG.md) — Development phase log
- [docs/CGW2_TELEGRAM_ROUTER.md](docs/CGW2_TELEGRAM_ROUTER.md) — Telegram router architecture
- [docs/HERMES_INTEGRATION.md](docs/HERMES_INTEGRATION.md) — Hermes / OpenClaw integration guide
- [docs/CGW3A_LIVE_ADAPTER_SKELETON.md](docs/CGW3A_LIVE_ADAPTER_SKELETON.md) — Live adapter skeleton and CGW-3A architecture
- [docs/CGW3B_LIVE_SMOKE.md](docs/CGW3B_LIVE_SMOKE.md) — Guarded live smoke requirements and commands

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Please keep changes focused — this is a glue layer, not an automation framework.

## Security

See [SECURITY.md](SECURITY.md) for security policies and vulnerability reporting.
