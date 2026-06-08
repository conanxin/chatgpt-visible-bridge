"""Telegram router for ChatGPT Visible Bridge.

Top-level entry point that combines parsing and handling.
"""

from __future__ import annotations

from typing import Optional

from ..workspace import Workspace
from .handler import TelegramHandler
from .parser import TelegramCommand, parse_command


class TelegramRouter:
    """Routes Telegram messages to the appropriate handler."""

    def __init__(self, workspace: Optional[Workspace] = None) -> None:
        self.handler = TelegramHandler(workspace)

    def route(self, message_text: str) -> str:
        """Parse a Telegram message and return the formatted response."""
        command = parse_command(message_text)
        return self.handler.handle(command)
