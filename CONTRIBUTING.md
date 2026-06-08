# Contributing to ChatGPT Visible Bridge

Thank you for your interest in contributing! This project is a glue layer, not a full automation framework. Please keep changes focused and minimal.

## How to Contribute

1. **Open an issue** first for significant changes or new features.
2. **Fork the repo** and create a feature branch.
3. **Write tests** for any new functionality.
4. **Update docs** if you change behavior.
5. **Run the test suite** before submitting.

## Development Setup

```bash
git clone https://github.com/conanxin/chatgpt-visible-bridge.git
cd chatgpt-visible-bridge
pip install -e .
python3 -m pytest tests/ -v
```

## Code Style

- Python 3.10+ standard library only (no heavy dependencies).
- Keep modules small and testable.
- Use type hints where practical.
- Follow existing patterns in the codebase.

## What We Need

- Bug fixes and edge-case handling.
- Documentation improvements.
- New adapter examples (no browser automation required).
- Better Telegram formatting for different platforms.

## What We Do Not Need

- Heavy frameworks or dependencies.
- Unattended daemon modes (watch mode is out of scope for now).
- Automatic execution of ChatGPT suggestions without explicit approval.

## Security

See [SECURITY.md](SECURITY.md) for security boundaries and vulnerability reporting.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
