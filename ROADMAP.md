# Roadmap

## Current Release: v0.1.0-alpha

**Status:** Alpha — open for feedback and real-world testing.

### What Works Now

- ✅ **Local task queue** — file-based `inbox/`/`active/`/`outbox/`/`failed/` with JSON tasks
- ✅ **CLI** — `create`, `status`, `worker-once`, `worker-drain`, `result`, `show`, `telegram-router`
- ✅ **Manual one-shot worker** — process one task, then exit; no daemon by default
- ✅ **Mock adapter** — default, safe, no network calls; returns structured responses
- ✅ **Telegram router simulation** — `/cgpt ask`, `/cgpt status`, `/cgpt result`, `/cgpt show`, `/cgpt help`
- ✅ **Guarded `codex-chatgpt-control` adapter** — blocked by default unless `--live` + `CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1`
- ✅ **Structured blocker reporting** — `browser_bridge_unavailable`, `dependency_missing`, `live_not_enabled`
- ✅ **75 tests** — all passing

### What Does Not Work Yet

- ❌ **Real visible ChatGPT Web live smoke** is **not confirmed** in the current WSL/Hermes runtime. A compatible browser bridge host (e.g., Codex Desktop) is required.
- ❌ **No default watch daemon** — intentional; one-shot by design
- ❌ **No file upload/download** — not implemented
- ❌ **No automatic local command execution** — consult-only by design
- ❌ **No `/agent approve` implementation** — requires explicit user confirmation in a future phase
- ❌ **No production Telegram bot** — the router is a library; a real gateway or bot is required for production use

---

## Near-Term Roadmap

### v0.1.1-alpha — Packaging and Installation Polish

- [ ] Clean `pip install` and editable install instructions
- [ ] Entry point cleanup and CLI naming consistency
- [ ] Clearer quick-start examples
- [ ] Smoke test command documentation
- [ ] Troubleshooting: `dependency_missing`, `browser_bridge_unavailable`, `live_not_enabled`

### v0.2.0-alpha — Real Browser-Host Live Smoke

- [ ] Run the guarded `codex-chatgpt-control` adapter from a **compatible browser bridge host** (e.g., Codex Desktop with ChatGPT Web already logged in)
- [ ] Confirm `VISIBLE_CHATGPT_BRIDGE_OK` smoke test passes through **real** ChatGPT Web
- [ ] Keep manual one-shot mode as default
- [ ] Keep no-upload / no-download boundary
- [ ] Record real adapter latency and blocker patterns

### v0.3.0-alpha — Telegram Full Loop

- [ ] `/cgpt ask` creates a real task
- [ ] User manually runs the live worker
- [ ] `/cgpt result` returns the **real** ChatGPT response or a structured blocker report
- [ ] No auto-execution by default
- [ ] No default watch daemon

### v0.4.0-alpha — Approval Flow Design

- [ ] Design `/agent approve` flow without auto-execution
- [ ] Generated command review before execution
- [ ] Explicit user confirmation per step
- [ ] Project-level allowlist
- [ ] Clear audit trail for every approved action

---

## Future / Backlog

- **Existing tab/thread reuse** — avoid opening a new browser tab for every task
- **Optional screenshots** — attach a screenshot of the ChatGPT response to the report
- **Optional local dashboard** — simple HTML/CLI dashboard for queue status and reports
- **Better adapter diagnostics** — richer error messages and environment checks
- **More agent integrations** — Discord, Slack, or other messaging platforms
- **PyPI packaging** — only after the live boundary is stable and well-tested

---

## Non-Goals

These are explicitly out of scope for this project:

- 🚫 **OpenAI API wrapper** — we target the ChatGPT Web interface, not `api.openai.com`
- 🚫 **Hidden/headless browser bot** — the browser must be visible and interruptible
- 🚫 **Login/captcha bypass** — we do not bypass authentication or anti-bot measures
- 🚫 **Token/cookie/session harvesting** — we do not store or extract credentials
- 🚫 **Unattended local command execution** — all execution requires explicit approval

---

## Version History

- **v0.1.0-alpha** — Task queue, CLI, mock worker, Telegram router, guarded live adapter, structured blocker reporting

---

For the latest release, see [GitHub Releases](https://github.com/conanxin/chatgpt-visible-bridge/releases).
