# CGW-3B Live Smoke

CGW-3B adds a guarded live smoke path for the `codex-chatgpt-control` adapter.

## Scope

- Manual one-shot worker only.
- Plain text prompt submission only.
- Markdown response capture into `outbox/` and `reports/`.
- No file upload.
- No file download.
- No watch daemon.
- No automatic execution of ChatGPT returned commands.
- No cookie, session, browser profile, or token reads.

## Runtime Requirement

The live path must run inside a compatible Codex/browser bridge host where the
documented `codex_chatgpt_control` Python package is importable and can operate
a visible logged-in ChatGPT Web page.

Ordinary shell execution is expected to return a structured blocked result,
usually `live_not_enabled`, `dependency_missing`, or
`browser_bridge_unavailable`. That is not a code failure when the blocked result
is written to `outbox/` and `reports/`.

## Commands

Non-live guard:

```bash
export CGW_HOME=/tmp/cgw3b-nonlive
rm -rf /tmp/cgw3b-nonlive

PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  python3 -m chatgpt_visible_bridge.cli create-task \
  --prompt "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"

PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  python3 -m chatgpt_visible_bridge.cli worker-once \
  --adapter codex-chatgpt-control
```

Expected: `blocked`; no real ChatGPT Web operation is attempted.

Live smoke:

```bash
export CGW_HOME=/tmp/cgw3b-live
rm -rf /tmp/cgw3b-live
export CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1

PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  python3 -m chatgpt_visible_bridge.cli create-task \
  --prompt "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"

PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  python3 -m chatgpt_visible_bridge.cli worker-once \
  --adapter codex-chatgpt-control \
  --live
```

Expected in a compatible host: `success`, with `response_markdown` and report
content containing `VISIBLE_CHATGPT_BRIDGE_OK`.

Acceptable blocker outside a compatible host: a structured blocked result with
`dependency_missing`, `browser_bridge_unavailable`, `login_required`,
`permission_required`, or `ui_state_unavailable`.

## Existing Tab Behavior

CGW-3B defaults to a new thread request when the package supports that option.
Existing tab/thread reuse is intentionally deferred to CGW-3C unless the
`codex_chatgpt_control` package supports it cleanly without selector scraping or
session inspection.
