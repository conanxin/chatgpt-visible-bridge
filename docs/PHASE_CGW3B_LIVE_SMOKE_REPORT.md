# Phase CGW-3B Live Smoke Report

## 1. Goal

Implement a guarded `codex-chatgpt-control` live adapter path for
`chatgpt-visible-bridge`, keep ordinary shell execution blocker-safe, and run
the minimum visible ChatGPT Web smoke flow when the environment supports it.

## 2. Environment Classification

**Compatible browser bridge host?** no for the current WSL runtime.

Evidence:
- `codex_chatgpt_control` Python package is not installed in this runtime.
- Tool discovery did not expose a Browser/Chrome bridge tool for direct visible
  ChatGPT Web control.
- Node REPL metadata showed Codex thread metadata only, not a browser bridge
  handle.

## 3. Files Changed

- `chatgpt_visible_bridge/adapters/codex_chatgpt_control.py`
- `chatgpt_visible_bridge/cli.py`
- `chatgpt_visible_bridge/schema.py`
- `chatgpt_visible_bridge/worker.py`
- `tests/test_adapters.py`
- `tests/test_cgw3a_blocked.py`
- `tests/test_cgw3b_live_adapter.py`
- `README.md`
- `docs/CGW3B_LIVE_SMOKE.md`
- `docs/PHASE_LOG.md`
- `docs/SECURITY_BOUNDARY.md`
- `docs/PHASE_CGW3B_LIVE_SMOKE_REPORT.md`

## 4. Adapter Implementation Summary

`CodexChatGPTControlAdapter` now has a guarded live path:

- Default behavior is `blocked/live_not_enabled`; it does not import or call
  `codex_chatgpt_control`.
- Live mode is enabled by `CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1`.
- Missing package returns `blocked/dependency_missing`.
- Package/bridge failure returns `blocked/browser_bridge_unavailable`.
- Package-reported blockers preserve stop reasons such as `login_required`,
  `permission_required`, or `ui_state_unavailable`.
- Success returns `status=success`, `adapter=codex-chatgpt-control`,
  `response_markdown`, a short `summary`, and `stop_reason=null`.

The adapter does not hardcode ChatGPT URL selectors, scrape private endpoints,
read cookies/sessions/browser profiles, upload files, download files, or
execute ChatGPT returned commands.

## 5. CLI Behavior

Supported live command:

```bash
python3 -m chatgpt_visible_bridge.cli worker-once \
  --adapter codex-chatgpt-control \
  --live
```

`--live` sets `CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1` only for that
`worker-once` invocation and restores the previous environment afterward.

Without `--live` or the live env var, the worker writes a blocked result and no
real ChatGPT Web operation is attempted.

## 6. Tests

Command:

```bash
cd /home/conanxin/chatgpt-visible-bridge
PYTHONPATH=/home/conanxin/chatgpt-visible-bridge python3 -m pytest tests/ -q
```

Result:

```text
75 passed in 0.90s
```

Coverage added:
- live flag off -> `blocked/live_not_enabled`
- dependency missing -> `blocked/dependency_missing`
- simulated bridge unavailable -> `blocked/browser_bridge_unavailable`
- mocked live success writes `response_markdown` to result/report
- mocked blocked path still writes result/report
- CLI `worker-once --live` temporarily enables live mode

## 7. Non-Live Guard Smoke Result

Commands:

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

Result:
- Task ID: `c0c5b31ce4dc4e6f`
- Status: `blocked`
- Adapter: `codex-chatgpt-control`
- Stop reason: `live_not_enabled`
- Report: `/tmp/cgw3b-nonlive/reports/c0c5b31ce4dc4e6f.md`
- Telegram router `/cgpt result c0c5b31ce4dc4e6f` displayed the blocked
  summary and report path.

No real ChatGPT Web operation was attempted.

## 8. Real Live Smoke Result

Commands:

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

Result:
- Task ID: `8942eabb0a154f32`
- Status: `blocked`
- Adapter: `codex-chatgpt-control`
- Stop reason: `dependency_missing`
- Report: `/tmp/cgw3b-live/reports/8942eabb0a154f32.md`
- Telegram router `/cgpt result 8942eabb0a154f32` displayed the blocked
  summary and report path.

Exact blocker summary:

```text
The Python package `codex_chatgpt_control` is not installed in this runtime.
```

NEXT_SAFE_COMMAND:

```bash
cd /home/conanxin/chatgpt-visible-bridge
export CGW_HOME=/tmp/cgw3b-live
export CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1
PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  python3 -m chatgpt_visible_bridge.cli worker-once \
  --adapter codex-chatgpt-control \
  --live
```

Run the command only after installing or exposing the documented
`codex_chatgpt_control` package in a compatible Codex/browser bridge host with
ChatGPT Web already logged in.

## 9. Security/Open-Source Check

Checks run:

- Telegram token / OpenAI key / hardcoded chat_id patterns
- cookie/session/browser profile references
- selector scraping references
- upload/download references
- tracked `.env` files

Result:
- No real token, API key, hardcoded chat_id, cookie, session, or browser
  profile path found in code.
- No ChatGPT selector scraping code found.
- No active upload/download code found; live kwargs explicitly pass
  `upload_files=False` and `download_files=False` when the package accepts
  those parameters.
- `.env` is not tracked. `.env.example` is tracked as a placeholder example.
- Search hits outside code were documentation/examples describing the security
  boundary.

## 10. Git Status Before Commit

```text
 M README.md
 M chatgpt_visible_bridge/adapters/codex_chatgpt_control.py
 M chatgpt_visible_bridge/cli.py
 M chatgpt_visible_bridge/schema.py
 M chatgpt_visible_bridge/worker.py
 M docs/PHASE_LOG.md
 M docs/SECURITY_BOUNDARY.md
 M tests/test_adapters.py
 M tests/test_cgw3a_blocked.py
?? docs/CGW3B_LIVE_SMOKE.md
?? docs/PHASE_CGW3B_LIVE_SMOKE_REPORT.md
?? tests/test_cgw3b_live_adapter.py
```

## 11. Commit Hash After Commit

Implementation commit:

```text
d47d8491421db0423984678a7abd5f132736e996
```

## 12. Remaining Limitations

- Current runtime cannot perform the visible ChatGPT Web operation because
  `codex_chatgpt_control` is missing.
- Existing tab/thread reuse is deferred.
- No file upload/download support.
- No watch daemon.
- No automatic execution mode.

## 13. CGW-3C Recommendation

- Add existing tab/thread reuse only if the SDK supports it cleanly.
- Run Telegram -> manual live worker -> `/cgpt result` as a full live flow.
- Keep no file upload/download in CGW-3C.
- Keep ChatGPT returned commands as text-only recommendations.

## 14. Go/No-Go Judgment

- **Code:** GO
- **Live environment:** NO-GO in this WSL runtime due to
  `dependency_missing`
- **Overall CGW-3B:** PASS as guarded live adapter smoke path with structured
  blocker-safe fallback
