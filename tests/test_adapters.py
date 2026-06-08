"""Tests for adapters/ package — adapter registry, mock, and codex-chatgpt-control skeleton."""

from chatgpt_visible_bridge.adapters import (
    CodexChatGPTControlAdapter,
    MockAdapter,
    get_adapter,
    list_adapters,
)
from chatgpt_visible_bridge.schema import ResultStatus, Task


def test_adapter_registry_includes_mock():
    adapter = get_adapter("mock")
    assert isinstance(adapter, MockAdapter)
    assert adapter.name == "mock"


def test_adapter_registry_includes_codex_chatgpt_control():
    adapter = get_adapter("codex-chatgpt-control")
    assert isinstance(adapter, CodexChatGPTControlAdapter)
    assert adapter.name == "codex-chatgpt-control"


def test_list_adapters():
    names = list_adapters()
    assert "mock" in names
    assert "codex-chatgpt-control" in names


def test_get_adapter_unknown():
    import pytest
    with pytest.raises(ValueError) as exc_info:
        get_adapter("nonexistent")
    assert "nonexistent" in str(exc_info.value)
    assert "mock" in str(exc_info.value)
    assert "codex-chatgpt-control" in str(exc_info.value)


def test_mock_adapter_smoke_prompt():
    adapter = MockAdapter()
    task = Task(prompt="请只回复 VISIBLE_CHATGPT_BRIDGE_OK")
    result = adapter.send(task)
    assert result.status == ResultStatus.SUCCESS
    assert "VISIBLE_CHATGPT_BRIDGE_OK" in result.summary
    assert result.adapter == "mock"
    assert result.stop_reason == "smoke_test_prompt"


def test_mock_adapter_generic_prompt():
    adapter = MockAdapter()
    task = Task(prompt="What is the best architecture?")
    result = adapter.send(task)
    assert result.status == ResultStatus.SUCCESS
    assert "mock adapter" in result.summary
    assert result.stop_reason == "mock_consult_only"


def test_codex_adapter_returns_blocked():
    adapter = CodexChatGPTControlAdapter()
    task = Task(prompt="请只回复 VISIBLE_CHATGPT_BRIDGE_OK")
    result = adapter.send(task)
    assert result.status == ResultStatus.BLOCKED
    assert result.adapter == "codex-chatgpt-control"
    assert result.stop_reason == "browser_bridge_unavailable"
    assert "CGW-3A Skeleton" in result.summary
    assert "CGW-3B" in result.suggested_next_action


def test_codex_adapter_not_available():
    adapter = CodexChatGPTControlAdapter()
    assert adapter.available is False


def test_codex_adapter_dry_run():
    import os
    old = os.environ.get("CGW_LIVE_ADAPTER_DRY_RUN")
    os.environ["CGW_LIVE_ADAPTER_DRY_RUN"] = "1"
    try:
        adapter = CodexChatGPTControlAdapter()
        task = Task(prompt="Test")
        result = adapter.send(task)
        assert result.status == ResultStatus.BLOCKED
        assert "dry-run" in result.summary.lower()
    finally:
        if old is None:
            os.environ.pop("CGW_LIVE_ADAPTER_DRY_RUN", None)
        else:
            os.environ["CGW_LIVE_ADAPTER_DRY_RUN"] = old


def test_backward_compat_adapter_import():
    """Ensure old import path still works."""
    from chatgpt_visible_bridge.adapter import get_adapter as old_get_adapter
    adapter = old_get_adapter("mock")
    assert adapter.name == "mock"


def test_backward_compat_live_adapter():
    """Ensure old 'live' adapter still works via backward-compat alias."""
    from chatgpt_visible_bridge.adapter import get_adapter as old_get_adapter
    adapter = old_get_adapter("live")
    assert adapter.name == "live"
