"""Telegram module for ChatGPT Visible Bridge.

Provides command parsing, formatting, and routing for Telegram /cgpt commands.
"""

from .formatter import (
    format_ask_error,
    format_ask_response,
    format_help,
    format_result,
    format_show,
    format_status,
    format_unknown,
)
from .handler import TelegramHandler
from .parser import TelegramCommand, TelegramCommandType, parse_command
from .router import TelegramRouter

__all__ = [
    "TelegramCommand",
    "TelegramCommandType",
    "parse_command",
    "TelegramHandler",
    "TelegramRouter",
    "format_ask_response",
    "format_ask_error",
    "format_status",
    "format_result",
    "format_show",
    "format_help",
    "format_unknown",
]
