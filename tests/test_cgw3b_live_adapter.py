"""CGW-3B guarded live adapter tests.

These tests never open ChatGPT Web. The codex_chatgpt_control package is
mocked so normal pytest remains offline and deterministic.
"""

import importlib
import tempfile
import types
from pathlib import Path

from chatgpt_visible_bridge.adapters.codex_chatgpt_control import (
    LIVE_ENV,
    CodexChatGPTControlAdapter,
)
from chatgpt_visible_bridge.cli import main
from chatgpt_visible_bridge.schema import ResultStatus, Task
from chatgpt_visible_bridge.workspace import Workspace
from chatgpt_visible_bridge.worker import Worker


def test_live_flag_off_blocks_without_import(monkeypatch):
    monkeypatch.delenv(LIVE_ENV, raising=False)

    def fail_import(name):
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr(importlib, "import_module", fail_import)

    result = CodexChatGPTControlAdapter().send(Task(prompt="hello"))

    assert result.status == ResultStatus.BLOCKED
    assert result.stop_reason == "live_not_enabled"
    assert "No real ChatGPT Web operation" in result.summary


def test_live_dependency_missing_blocks(monkeypatch):
    monkeypatch.setenv(LIVE_ENV, "1")

    def missing_import(name):
        if name == "codex_chatgpt_control":
            raise ImportError(name)
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", missing_import)

    result = CodexChatGPTControlAdapter().send(Task(prompt="hello"))

    assert result.status == ResultStatus.BLOCKED
    assert result.stop_reason == "dependency_missing"
    assert "not installed" in result.summary


def test_live_bridge_unavailable_blocks(monkeypatch):
    monkeypatch.setenv(LIVE_ENV, "1")
    fake_control = types.SimpleNamespace(
        send_prompt=lambda **kwargs: (_ for _ in ()).throw(RuntimeError("bridge offline"))
    )
    monkeypatch.setattr(importlib, "import_module", lambda name: fake_control)

    result = CodexChatGPTControlAdapter().send(Task(prompt="hello"))

    assert result.status == ResultStatus.BLOCKED
    assert result.stop_reason == "browser_bridge_unavailable"
    assert "bridge offline" in result.summary


def test_live_success_path_writes_response_markdown(monkeypatch):
    monkeypatch.setenv(LIVE_ENV, "1")
    fake_control = types.SimpleNamespace(
        send_prompt=lambda **kwargs: {
            "status": "success",
            "response_markdown": "VISIBLE_CHATGPT_BRIDGE_OK",
        }
    )
    monkeypatch.setattr(importlib, "import_module", lambda name: fake_control)

    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        task = Task(prompt="请只回复 VISIBLE_CHATGPT_BRIDGE_OK")
        task.save(ws.task_path(task.id))

        result = Worker(ws, CodexChatGPTControlAdapter()).process_one()

        assert result is not None
        assert result.status == ResultStatus.SUCCESS
        assert result.stop_reason is None
        assert result.response_markdown == "VISIBLE_CHATGPT_BRIDGE_OK"
        assert "VISIBLE_CHATGPT_BRIDGE_OK" in ws.result_path(task.id).read_text(encoding="utf-8")
        assert "Response Markdown" in ws.report_path(task.id).read_text(encoding="utf-8")


def test_live_blocked_path_still_writes_result(monkeypatch):
    monkeypatch.setenv(LIVE_ENV, "1")
    fake_control = types.SimpleNamespace(
        send_prompt=lambda **kwargs: {
            "status": "blocked",
            "stop_reason": "login_required",
            "summary": "ChatGPT login is required.",
            "next_action": "Open ChatGPT Web, log in, then rerun live smoke.",
        }
    )
    monkeypatch.setattr(importlib, "import_module", lambda name: fake_control)

    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        task = Task(prompt="hello")
        task.save(ws.task_path(task.id))

        result = Worker(ws, CodexChatGPTControlAdapter()).process_one()

        assert result is not None
        assert result.status == ResultStatus.BLOCKED
        assert result.stop_reason == "login_required"
        assert ws.result_path(task.id).exists()
        assert ws.failed_path(task.id).exists()


def test_cli_worker_once_live_sets_env_temporarily(monkeypatch):
    monkeypatch.delenv(LIVE_ENV, raising=False)
    fake_control = types.SimpleNamespace(send_prompt=lambda **kwargs: "VISIBLE_CHATGPT_BRIDGE_OK")
    monkeypatch.setattr(importlib, "import_module", lambda name: fake_control)

    with tempfile.TemporaryDirectory() as tmp:
        old_home = os_environ_get("CGW_HOME")
        set_os_environ("CGW_HOME", tmp)
        try:
            main(["create-task", "--prompt", "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"])
            ret = main(["worker-once", "--adapter", "codex-chatgpt-control", "--live"])
            assert ret == 0

            ws = Workspace(root=Path(tmp))
            result_path = ws.outbox_results()[0]
            assert "VISIBLE_CHATGPT_BRIDGE_OK" in result_path.read_text(encoding="utf-8")
            assert os_environ_get(LIVE_ENV) is None
        finally:
            restore_os_environ("CGW_HOME", old_home)


def os_environ_get(key):
    import os

    return os.environ.get(key)


def set_os_environ(key, value):
    import os

    os.environ[key] = value


def restore_os_environ(key, value):
    import os

    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value
