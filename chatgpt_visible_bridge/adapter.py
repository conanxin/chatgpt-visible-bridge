"""Adapter interface for ChatGPT Visible Bridge.

DEPRECATED: This module is kept for backward compatibility.
Use `chatgpt_visible_bridge.adapters` instead.
"""

from __future__ import annotations

from .adapters import (  # noqa: F401
    Adapter,
    CodexChatGPTControlAdapter,
    MockAdapter,
    list_adapters,
)
from .adapters.registry import get_adapter as _get_adapter


# Re-export LiveAdapter as a backward-compatible alias for the old name
class LiveAdapter(CodexChatGPTControlAdapter):
    """Backward-compatible alias for CodexChatGPTControlAdapter."""
    name = "live"


def get_adapter(name: str):
    """Backward-compatible adapter factory.

    Maps old 'live' name to 'codex-chatgpt-control' for compatibility.
    """
    if name == "live":
        return LiveAdapter()
    return _get_adapter(name)