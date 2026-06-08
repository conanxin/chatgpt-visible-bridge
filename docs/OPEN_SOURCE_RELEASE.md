# Open Source Release Plan

## Current Status: MVP (v0.1.0)

This is a **minimum viable product** for community feedback. It is intentionally minimal to validate the core concept before building more features.

## Release Checklist

### Code

- [x] Project skeleton (README, LICENSE, .gitignore)
- [x] Task and Result JSON schemas
- [x] Mock adapter with structured responses
- [x] Live adapter placeholder (blocked by default)
- [x] One-shot worker (once + drain)
- [x] CLI commands (create, status, worker, result, show)
- [x] File-based workspace management
- [x] Tests for core functionality

### Documentation

- [x] README.md with architecture overview
- [x] docs/ARCHITECTURE.md
- [x] docs/TASK_CONTRACT.md
- [x] docs/TELEGRAM_WORKFLOW.md
- [x] docs/WORKER_MODES.md
- [x] docs/SECURITY_BOUNDARY.md
- [x] docs/PHASE_LOG.md
- [x] examples/task.example.json
- [x] examples/result.example.json
- [x] examples/telegram-commands.md

### Quality

- [x] MIT License
- [x] .env.example (no real credentials)
- [x] .gitignore excludes sensitive files
- [x] Tests pass locally
- [x] CLI smoke tests pass

### Roadmap to v1.0

| Milestone | Description | Status |
|-----------|-------------|--------|
| v0.1.0-alpha | Core pipeline, CLI, mock adapter, Telegram router, guarded live adapter | ✅ Done |
| v0.1.1-alpha | Packaging and installation polish | Planned |
| v0.2.0-alpha | Real browser-host live smoke from Codex Desktop / compatible host | Planned |
| v0.3.0-alpha | Telegram full loop with real results | Planned |
| v0.4.0-alpha | Approval flow design (`/agent approve`) | Planned |
| v1.0.0 | Stable API, full documentation, community tested | Target |

For the full roadmap, see [ROADMAP.md](../ROADMAP.md).

## Contributing

We welcome feedback and contributions. Please keep the scope focused:

- This is a **glue layer**, not a full automation framework.
- Prefer **simplicity and auditability** over feature richness.
- All new features must include tests and documentation.

## License

MIT — see [LICENSE](../LICENSE).
