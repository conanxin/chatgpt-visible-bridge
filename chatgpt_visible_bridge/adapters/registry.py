"""Adapter registry for ChatGPT Visible Bridge.

Factory to get adapter instances by name.
"""

from __future__ import annotations

from .base import Adapter
from .codex_chatgpt_control import CodexChatGPTControlAdapter
from .mock import MockAdapter


# Built-in adapter registry
_ADAPTERS: dict[str, Adapter] = {
    "mock": MockAdapter(),
    "codex-chatgpt-control": CodexChatGPTControlAdapter(),
}


def get_adapter(name: str) -> Adapter:
    """Factory to get an adapter by name.

    Args:
        name: Adapter name ("mock" or "codex-chatgpt-control")

    Returns:
        Adapter instance

    Raises:
        ValueError: If the adapter name is not registered
    """
    if name not in _ADAPTERS:
        raise ValueError(
            f"Unknown adapter: {name}. "
            f"Available: {list(_ADAPTERS.keys())}"
        )
    return _ADAPTERS[name]


def list_adapters() -> list[str]:
    """Return list of registered adapter names."""
    return list(_ADAPTERS.keys())
