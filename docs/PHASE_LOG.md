# Phase Log

## Phase CGW-0 → CGW-1: MVP Creation

**Date:** 2026-06-08
**Goal:** Build the minimum viable product for the ChatGPT Visible Bridge.

### What Was Built

1. **Project skeleton**
   - `README.md` with clear "what this is / what this is not" statements
   - `LICENSE` (MIT)
   - `.gitignore` excluding credentials and runtime data
   - `.env.example` with placeholder values only

2. **Core Python package**
   - `chatgpt_visible_bridge/schema.py` — Task and Result dataclasses with JSON serialization
   - `chatgpt_visible_bridge/workspace.py` — File-based workspace management
   - `chatgpt_visible_bridge/adapter.py` — Adapter interface with MockAdapter and LiveAdapter placeholder
   - `chatgpt_visible_bridge/worker.py` — One-shot worker logic
   - `chatgpt_visible_bridge/cli.py` — CLI with subcommand detection from script name
   - `chatgpt_visible_bridge/__init__.py` — Package version

3. **CLI commands**
   - `cgpt-create-task` — Create task in inbox
   - `cgpt-task-status` — Show queue status
   - `cgpt-worker-once` — Process one task and exit
   - `cgpt-worker-drain` — Process all tasks and exit
   - `cgpt-task-result` — Show result JSON and report
   - `cgpt-task-show` — Show original prompt and wrapped prompt

4. **Documentation**
   - `docs/ARCHITECTURE.md` — System design and data flow
   - `docs/TASK_CONTRACT.md` — Task and Result JSON schemas
   - `docs/TELEGRAM_WORKFLOW.md` — Telegram integration guide
   - `docs/WORKER_MODES.md` — Worker modes and adapter behavior
   - `docs/SECURITY_BOUNDARY.md` — Security and trust boundaries
   - `docs/OPEN_SOURCE_RELEASE.md` — Release plan and roadmap
   - `docs/PHASE_LOG.md` — This file

5. **Examples**
   - `examples/task.example.json` — Example task JSON
   - `examples/result.example.json` — Example result JSON
   - `examples/telegram-commands.md` — Telegram command reference

6. **Tests**
   - `tests/test_schema.py` — Schema serialization/deserialization
   - `tests/test_workspace.py` — Workspace directory creation
   - `tests/test_worker.py` — Worker lifecycle (claim, process, result, fail)
   - `tests/test_cli.py` — CLI smoke tests

### Design Decisions

- **Python over Node**: Faster implementation, fewer dependencies, stdlib covers most needs.
- **File-based queue over database**: Simplicity, auditability, no external dependencies.
- **Mock adapter default**: Allows full pipeline testing without touching ChatGPT Web.
- **Live adapter blocked**: Explicitly prevents accidental real Web usage in MVP.
- **One-shot worker**: Manual execution is the default; no daemon mode.
- **Consult-only default**: No automatic execution of ChatGPT suggestions.
- **CLI entry points via pyproject.toml**: Clean installation with `pip install -e .`.

### Known Limitations (Intentional)

- No real ChatGPT Web adapter (MVP scope).
- No Telegram bot wrapper (planned for v0.2.0).
- No execution mode (`policy.allow_execute` exists but is not implemented).
- No file upload support.
- No retry logic for failed tasks.
- No task templates or batch creation.

## Phase CGW-2: Telegram Router

**Date:** 2026-06-08
**Goal:** Add Telegram command routing layer to the ChatGPT Visible Bridge.

### What Was Built

1. **Telegram module** (`chatgpt_visible_bridge/telegram/`)
   - `parser.py` — Parses `/cgpt` commands into structured `TelegramCommand` objects
   - `handler.py` — Connects commands to the file-based task queue
   - `formatter.py` — Formats Telegram-friendly responses (emoji, bullets, no tables)
   - `router.py` — One-liner convenience: `parse + handle + format`
   - `__init__.py` — Clean public API exports

2. **Supported commands**
   - `/cgpt ask <prompt>` — Creates `consult_only` task in inbox
   - `/cgpt status` — Shows queue counts + recent task IDs
   - `/cgpt result <task_id>` — Shows result summary + report path
   - `/cgpt show <task_id>` — Shows task metadata + original prompt
   - `/cgpt help` — Shows usage instructions
   - Unknown/invalid — Returns error + help text

3. **CLI integration**
   - Added `cgpt-telegram-router` command to `cli.py`
   - Added entry point to `pyproject.toml`
   - Usage: `python3 -m chatgpt_visible_bridge.cli telegram-router "/cgpt ask Hello"`

4. **Tests** (28 new tests, 52 total)
   - `tests/test_telegram_parser.py` — 17 parser unit tests
   - `tests/test_telegram_handler.py` — 11 integration tests with temp CGW_HOME
   - All 52 tests pass

5. **Documentation**
   - `docs/CGW2_TELEGRAM_ROUTER.md` — Router architecture and usage
   - `docs/HERMES_INTEGRATION.md` — Integration guide for OpenClaw/Hermes
   - Updated `docs/TELEGRAM_WORKFLOW.md` — Current command status

### Design Decisions

- **No real Telegram API**: The router is a library, not a bot. It can be used by any Telegram framework or gateway.
- **Consult-only enforcement**: All `/cgpt ask` tasks create tasks with `allow_execute=false` and `allow_upload_files=false`.
- **Telegram-friendly formatting**: No markdown tables, emoji + bullet lists, safe truncation for long prompts.
- **Temp CGW_HOME in tests**: All integration tests use temporary directories, never touching the real workspace.

### Known Limitations (Intentional)

- No real Telegram bot implementation (out of scope for CGW-2).
- No OpenClaw/Hermes plugin implementation (this is a library, not a plugin).
- No execution mode (`/agent approve` still not implemented).
- No file upload support.

### Next Phase Ideas

- CGW-3: Live adapter integration with `codex-chatgpt-control` or similar browser bridge.

---