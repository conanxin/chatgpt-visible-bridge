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

### Next Phase Ideas

- CGW-2: Telegram bot wrapper that reads/writes the same file-based queue.
- CGW-3: Live adapter integration with codex-chatgpt-control or Playwright bridge.
- CGW-4: Task templates, batch creation, and retry logic.
