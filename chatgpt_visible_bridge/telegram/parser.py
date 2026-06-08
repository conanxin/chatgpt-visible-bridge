"""Telegram command parser for ChatGPT Visible Bridge.

Parses Telegram /cgpt messages into structured command objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class TelegramCommandType(Enum):
    ASK = auto()
    STATUS = auto()
    RESULT = auto()
    SHOW = auto()
    HELP = auto()
    UNKNOWN = auto()


@dataclass
class TelegramCommand:
    type: TelegramCommandType
    raw_text: str
    prompt: Optional[str] = None
    task_id: Optional[str] = None
    error: Optional[str] = None


def parse_command(text: str) -> TelegramCommand:
    """Parse a Telegram message text into a TelegramCommand.

    Supported commands:
      /cgpt ask <prompt>       -> ASK, prompt
      /cgpt status             -> STATUS
      /cgpt result <task_id>   -> RESULT, task_id
      /cgpt show <task_id>     -> SHOW, task_id
      /cgpt help               -> HELP
      /cgpt <unknown>          -> UNKNOWN
    """
    text = text.strip()

    # Must start with /cgpt
    if not text.startswith("/cgpt"):
        return TelegramCommand(
            type=TelegramCommandType.UNKNOWN,
            raw_text=text,
            error="Message must start with /cgpt",
        )

    # Remove the /cgpt prefix and leading space
    rest = text[len("/cgpt"):].strip()

    if not rest:
        return TelegramCommand(
            type=TelegramCommandType.UNKNOWN,
            raw_text=text,
            error="Missing subcommand after /cgpt",
        )

    parts = rest.split(maxsplit=1)
    subcommand = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else None

    if subcommand == "ask":
        if not arg or not arg.strip():
            return TelegramCommand(
                type=TelegramCommandType.UNKNOWN,
                raw_text=text,
                error="Missing prompt after /cgpt ask",
            )
        return TelegramCommand(
            type=TelegramCommandType.ASK,
            raw_text=text,
            prompt=arg.strip(),
        )

    elif subcommand == "status":
        return TelegramCommand(
            type=TelegramCommandType.STATUS,
            raw_text=text,
        )

    elif subcommand == "result":
        if not arg or not arg.strip():
            return TelegramCommand(
                type=TelegramCommandType.UNKNOWN,
                raw_text=text,
                error="Missing task_id after /cgpt result",
            )
        return TelegramCommand(
            type=TelegramCommandType.RESULT,
            raw_text=text,
            task_id=arg.strip().split()[0],  # take first token only
        )

    elif subcommand == "show":
        if not arg or not arg.strip():
            return TelegramCommand(
                type=TelegramCommandType.UNKNOWN,
                raw_text=text,
                error="Missing task_id after /cgpt show",
            )
        return TelegramCommand(
            type=TelegramCommandType.SHOW,
            raw_text=text,
            task_id=arg.strip().split()[0],  # take first token only
        )

    elif subcommand == "help":
        return TelegramCommand(
            type=TelegramCommandType.HELP,
            raw_text=text,
        )

    else:
        return TelegramCommand(
            type=TelegramCommandType.UNKNOWN,
            raw_text=text,
            error=f"Unknown subcommand: {subcommand}",
        )
