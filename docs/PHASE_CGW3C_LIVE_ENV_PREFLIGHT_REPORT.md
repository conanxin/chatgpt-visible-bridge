# Phase CGW-3C Live Environment Preflight Report

## Goal

Validate the current Codex/browser host environment for
`chatgpt-visible-bridge`, install the live adapter dependencies if possible,
confirm the non-live guard still blocks safely, and attempt the minimum visible
ChatGPT Web smoke test.

## Environment Classification

**Compatible browser bridge host?** no for the current runtime.

Evidence:

- `python3` runs in an Ubuntu externally-managed environment and rejected the
  requested system-level pip install.
- `codex_chatgpt_control` remains missing from the `python3` import path.
- Node REPL preflight found no `globalThis.agent`, `globalThis.browser`, or
  `globalThis.chrome`.
- Current tool discovery did not expose a Browser/Chrome bridge handle for
  direct visible ChatGPT Web control.

Chrome/ChatGPT login state could not be verified from this runtime without a
browser bridge. No cookies, sessions, browser profiles, or tokens were read.

## Dependency Install Result

Requested Python command:

```bash
python3 -m pip install codex-chatgpt-control
```

Result: failed.

Stop reason:

```text
dependency_install_failed
```

Exact blocker:

```text
error: externally-managed-environment
```

Requested npm command:

```bash
npm install codex-chatgpt-control
```

Result: failed.

Exact blocker:

```text
npm error Tracker "idealTree" already exists
```

No `package.json`, `package-lock.json`, or `node_modules` was added to the repo.

NEXT_SAFE_COMMAND:

```bash
cd /home/conanxin/chatgpt-visible-bridge
python3 -m venv .venv-cgw-live
. .venv-cgw-live/bin/activate
python -m pip install --upgrade pip
python -m pip install codex-chatgpt-control
npm install codex-chatgpt-control
PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1 \
  CGW_HOME=/tmp/cgw3c-live \
  python -m chatgpt_visible_bridge.cli worker-once \
  --adapter codex-chatgpt-control \
  --live
```

Use this only in a compatible Codex/browser bridge host with ChatGPT Web already
logged in. Do not use `--break-system-packages` unless the operator explicitly
chooses to risk modifying the system Python environment.

## Test Result

Command:

```bash
cd /home/conanxin/chatgpt-visible-bridge
PYTHONPATH=/home/conanxin/chatgpt-visible-bridge python3 -m pytest tests/ -q
```

Result:

```text
75 passed in 0.62s
```

## Non-Live Guard Smoke Result

Commands:

```bash
export CGW_HOME=/tmp/cgw3c-nonlive
rm -rf /tmp/cgw3c-nonlive
PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  python3 -m chatgpt_visible_bridge.cli create-task \
  --prompt "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"
PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  python3 -m chatgpt_visible_bridge.cli worker-once \
  --adapter codex-chatgpt-control
```

Result:

- Task ID: `55dd73931ff54ab7`
- Status: `blocked`
- Adapter: `codex-chatgpt-control`
- Stop reason: `live_not_enabled`
- Report: `/tmp/cgw3c-nonlive/reports/55dd73931ff54ab7.md`
- `/cgpt result 55dd73931ff54ab7` displayed the blocked result and report path.

No real ChatGPT Web operation was attempted.

## Live Preflight Result

Node REPL probe:

```json
{
  "hasAgent": false,
  "agentType": "undefined",
  "hasBrowser": false,
  "browserType": "undefined",
  "hasChrome": false,
  "chromeType": "undefined"
}
```

Result:

```text
browser_bridge_unavailable
```

Because the Python package install also failed, the adapter-level live smoke
reported `dependency_missing` before it could reach browser bridge control.

## Live Smoke Result

Commands:

```bash
export CGW_HOME=/tmp/cgw3c-live
rm -rf /tmp/cgw3c-live
export CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1
PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  python3 -m chatgpt_visible_bridge.cli create-task \
  --prompt "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"
PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  python3 -m chatgpt_visible_bridge.cli worker-once \
  --adapter codex-chatgpt-control \
  --live
PYTHONPATH=/home/conanxin/chatgpt-visible-bridge \
  python3 -m chatgpt_visible_bridge.cli task-status
```

Result:

- Task ID: `c73f851de81f4034`
- Status: `blocked`
- Adapter: `codex-chatgpt-control`
- Adapter stop reason: `dependency_missing`
- Preflight stop reason: `browser_bridge_unavailable`
- Report: `/tmp/cgw3c-live/reports/c73f851de81f4034.md`
- Queue status: inbox `0`, active `0`, outbox `1`, failed `1`
- `/cgpt result c73f851de81f4034` displayed the blocked result and report path.

Adapter next action:

```text
Install or expose the documented codex-chatgpt-control Python package in this
Codex/browser bridge host, then rerun worker-once --adapter
codex-chatgpt-control --live.
```

## Security Check

Checks run:

- Telegram token / OpenAI API key / hardcoded chat_id patterns
- cookie/session/browser profile references
- selector scraping references
- upload/download references
- tracked `.env` files

Result:

- No new real token, API key, cookie, session, browser profile path, or
  hardcoded chat_id was found.
- No selector scraping code was added.
- No upload/download code was added.
- `.env` is not tracked; only `.env.example` is tracked.
- Search hits were existing documentation/examples or existing safety fields
  such as `allow_upload_files` and `upload_files=False` /
  `download_files=False`.

## Git Status

Initial status before CGW-3C work:

```text
## master
```

Latest commits before CGW-3C:

```text
8a88e89 docs: update CGW-3B report with commit hash
d47d849 Implement codex ChatGPT control live adapter smoke path
c9d1b19 docs: final CGW-3A report with commit hash
f964216 docs: update CGW-3A report with final commit hash
bc4e294 Add live adapter skeleton for ChatGPT visible bridge
```

Status before writing this report:

```text
clean
```

## Code Changes

Project code changed: no.

Documentation changed: yes, this report was added.

## Commit

A documentation commit should be created for this report:

```text
Document live environment preflight for ChatGPT visible bridge
```

No git push should be performed.

## Go/No-Go

- **Code:** GO
- **Live environment:** NO-GO

CGW-3C status: PASS as an environment preflight with structured blockers.

Blocking reasons:

- `dependency_install_failed` for requested dependency installation.
- `browser_bridge_unavailable` from runtime preflight.
- `dependency_missing` from the guarded live smoke adapter path.
