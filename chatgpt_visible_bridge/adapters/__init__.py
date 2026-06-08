"""Adapter package for ChatGPT Visible Bridge.

Provides pluggable adapters for sending prompts to ChatGPT and receiving responses.
"""

from .base import Adapter
from .codex_chatgpt_control import CodexChatGPTControlAdapter
from .mock import MockAdapter
from .registry import get_adapter, list_adapters

__all__ = [
    "Adapter",
    "MockAdapter",
    "CodexChatGPTControlAdapter",
    "get_adapter",
    "list_adapters",
]
