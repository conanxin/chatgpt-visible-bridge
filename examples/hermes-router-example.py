#!/usr/bin/env python3
"""Generic Hermes / OpenClaw Router Example for ChatGPT Visible Bridge.

This is a conceptual example showing how an existing Hermes or OpenClaw
Telegram gateway could intercept /cgpt messages and route them to the
chatgpt-visible-bridge TelegramRouter without needing a separate bot.

NOTES:
- This is a generic example. No real token, chat_id, or private path is hardcoded.
- CGW_HOME is read from the environment or falls back to the default path.
- The parent gateway (Hermes/OpenClaw) manages Telegram authentication.
- The router only creates/reads local files; it does not execute commands.
- All tasks are consult-only by default (allow_execute=false, allow_upload_files=false).
"""

import os
from pathlib import Path

from chatgpt_visible_bridge.telegram import TelegramRouter


def get_cgw_home() -> Path:
    """Return the CGW workspace directory from environment or default."""
    env = os.getenv("CGW_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return Path.home() / ".openclaw" / "workspace" / "chatgpt-visible-bridge"


# Initialize the router with the workspace
cgw_home = get_cgw_home()
router = TelegramRouter(workspace=None)  # Uses CGW_HOME from environment


def handle_hermes_message(message_text: str) -> str | None:
    """Example Hermes message handler.

    This function intercepts /cgpt messages and routes them to the
    ChatGPT Visible Bridge. Non-/cgpt messages return None so they can
    be handled by other Hermes routers.

    Args:
        message_text: The raw text of the Telegram message.

    Returns:
        A Telegram-friendly response string, or None if the message is not /cgpt.
    """
    if not message_text.strip().startswith("/cgpt"):
        # Not a CGW command; let other Hermes handlers process it.
        return None

    # Route the message through the Telegram Router
    response = router.route(message_text)
    return response


def main():
    """Example local simulation without a real Telegram connection."""
    print(f"CGW Home: {cgw_home}")
    print()

    # Simulate Telegram messages
    test_messages = [
        '/cgpt ask "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"',
        '/cgpt status',
        '/cgpt result nonexistent123',
        '/cgpt help',
        '/cgpt delete something',  # Unknown command
    ]

    for msg in test_messages:
        print(f"--- Input: {msg} ---")
        response = handle_hermes_message(msg)
        if response is not None:
            print(response)
        else:
            print("(No CGW response; message passed to other handlers)")
        print()


if __name__ == "__main__":
    main()
