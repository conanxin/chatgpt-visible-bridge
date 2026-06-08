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

## Phase CGW-3A: Live Adapter Skeleton

**Date:** 2026-06-08
**Goal:** Add adapter-based worker architecture and codex-chatgpt-control adapter skeleton.

### What Was Built

1. **Adapter package** (`chatgpt_visible_bridge/adapters/`)
   - `base.py` — Adapter ABC with `send()` and `available` properties
   - `mock.py` — MockAdapter (unchanged behavior, default)
   - `codex_chatgpt_control.py` — CodexChatGPTControlAdapter skeleton (returns blocked by default)
   - `registry.py` — `get_adapter()` factory and `list_adapters()`
   - `__init__.py` — Public API exports

2. **Backward compatibility**
   - Old `chatgpt_visible_bridge.adapter` module re-exports from new package
   - `LiveAdapter` alias preserved for backward compatibility
   - All existing 52 tests continue to pass

3. **CLI adapter support**
   - `cgpt-worker-once --adapter mock` (explicit)
   - `cgpt-worker-once --mock` (backward compat)
   - `cgpt-worker-once --adapter codex-chatgpt-control` (skeleton, blocked)
   - `cgpt-worker-drain --adapter <name>` (same options)

4. **CodexChatGPTControlAdapter behavior (CGW-3A)**
   - Returns `blocked` status with `stop_reason: browser_bridge_unavailable`
   - Detailed summary explaining CGW-3A skeleton status
   - Points to CGW-3B for real live smoke from compatible browser bridge host
   - Optional `CGW_LIVE_ADAPTER_DRY_RUN=1` for dry-run blocked result
   - No real ChatGPT Web operation, no browser launch, no network calls

5. **Blocked result handling**
   - Writes report.md with full blocker explanation
   - Writes result.json with blocked status and stop_reason
   - Moves task to `failed/` with BLOCKED status
   - Telegram router displays blocked result with summary and next action

6. **Tests** (17 new tests, 69 total)
   - `test_adapters.py` — 11 adapter unit tests (registry, mock, codex, backward compat)
   - `test_cgw3a_blocked.py` — 6 integration tests (blocked result, report, Telegram display, CLI)
   - All 69 tests pass

7. **Documentation**
   - `docs/CGW3A_LIVE_ADAPTER_SKELETON.md` — Adapter architecture and CGW-3A behavior
   - Updated `docs/ARCHITECTURE.md` — Adapter layer section
   - Updated `docs/WORKER_MODES.md` — Adapter selection and live mode
   - Updated `README.md` — Live adapter skeleton section and CLI adapter options
   - Added `examples/adapter-commands.md` — Adapter command reference

### Design Decisions

- **Adapter-based architecture**: Worker now uses pluggable adapters, making it easy to add new ChatGPT interfaces in the future.
- **Skeleton-first**: CGW-3A implements the adapter interface and blocked behavior before attempting real browser automation. This ensures safe failure paths are tested before any real ChatGPT Web interaction.
- **No real network/browser in CGW-3A**: The codex-chatgpt-control adapter is intentionally blocked. Real live smoke requires a compatible browser bridge host (CGW-3B).
- **Backward compatibility preserved**: Old import paths and `--mock` flag continue to work.

### Known Limitations (Intentional)

- No real ChatGPT Web adapter (CGW-3A scope; CGW-3B will implement).
- No real browser automation (blocked by default in skeleton).
- No file upload/download support.
- No execution mode (`/agent approve` still not implemented).

### Next Phase Ideas

- CGW-3B: Real live smoke from Codex Desktop / compatible browser bridge host using codex-chatgpt-control.

---

## Phase CGW-3B: Guarded Live Adapter Smoke Path

**Date:** 2026-06-08
**Goal:** Extend `CodexChatGPTControlAdapter` from skeleton-only blocker into a guarded real live smoke adapter path.

### What Was Built

1. **Guarded live adapter path**
   - `CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1` enables live mode.
   - `worker-once --adapter codex-chatgpt-control --live` enables live mode for that one command.
   - Without explicit live enablement, the adapter returns `blocked/live_not_enabled` and does not import or call `codex_chatgpt_control`.
   - Missing package returns `blocked/dependency_missing`.
   - Bridge or UI failures return structured blockers such as `browser_bridge_unavailable`, `login_required`, or `ui_state_unavailable`.

2. **Response persistence**
   - Successful live responses include `response_markdown` in result JSON.
   - Worker reports include a `Response Markdown` section when present.
   - Telegram `/cgpt result <task_id>` continues to display the result summary and report path.

3. **Safety posture**
   - No file upload or download.
   - No ChatGPT selectors or private endpoint scraping.
   - No cookie, session, browser profile, token, or chat_id access.
   - No automatic execution of ChatGPT returned commands.
   - Still manual one-shot; no watch daemon.

4. **Tests**
   - Ordinary pytest uses mocked `codex_chatgpt_control` only.
   - Live flag off, dependency missing, bridge unavailable, live success, blocked result writing, and CLI `--live` behavior are covered.

5. **Documentation**
   - Added `docs/CGW3B_LIVE_SMOKE.md`.
   - Updated `README.md`.
   - Updated `docs/SECURITY_BOUNDARY.md`.

### Design Decisions

- **Explicit live gate**: The adapter does not attempt real ChatGPT Web operation unless live mode is explicitly enabled.
- **Dependency is optional**: `codex_chatgpt_control` is imported only on the live path. Missing dependency is a normal blocked result, not a crash.
- **Package API only**: The adapter calls documented package-level/client-level prompt methods if available. It does not hardcode ChatGPT DOM selectors.
- **New thread default**: CGW-3B requests a new thread when supported. Existing tab/thread reuse is deferred to CGW-3C.

### Known Limitations

- Live smoke succeeds only in a compatible Codex/browser bridge host with the `codex_chatgpt_control` package available and ChatGPT Web logged in.
- Existing tab/thread reuse is not guaranteed in CGW-3B.
- No file upload/download support.
- No execution mode.

### Next Phase Ideas

- CGW-3C: Existing tab/thread reuse if the SDK supports it cleanly.
- CGW-3C: Telegram -> manual live worker -> `/cgpt result` end-to-end live flow.
- Continue preserving no-file-upload and no-auto-execution boundaries.

---
