# Security Policy

## Supported Versions

| Version | Status |
|---------|--------|
| v0.1.0-alpha | Alpha — security updates as needed |

## Reporting a Vulnerability

Please report security vulnerabilities by opening a **private issue** on GitHub or by contacting the maintainers directly. Do not post security issues publicly.

## Security Boundaries

- **No credential storage**: Do not commit tokens, cookies, session data, or browser profiles to the repository. `.env` is in `.gitignore` for this reason.
- **No automatic execution**: ChatGPT-generated suggestions are saved as text only. No command is executed without explicit user approval.
- **No unattended browser**: The worker is one-shot and manual. No daemon or background browser session.
- **Live adapter is guarded**: Real ChatGPT Web interaction requires explicit `--live` flag and `CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE=1`. It must run in a visible browser window (headful) and be interruptible by the user.
- **No file upload/download**: Not implemented in the current version.
- **No hidden API scraping**: The project does not bypass login, captcha, or permissions.

## What This Project Does NOT Do

- It does not bypass ChatGPT login or captcha.
- It does not scrape the ChatGPT API using hidden endpoints.
- It does not store your OpenAI account credentials.
- It does not execute local commands suggested by ChatGPT without your explicit approval.

## If You Find Something Suspicious

1. Stop using the affected version immediately.
2. Report the issue privately.
3. Do not disclose details publicly until a fix is released.

## Security Scan Checklist (for maintainers)

Before each release:
- [ ] No token/cookie/session strings in code.
- [ ] No hardcoded chat_id or API keys.
- [ ] No browser profile paths in repo.
- [ ] `.env` not tracked by git.
- [ ] Examples are generic and safe.
