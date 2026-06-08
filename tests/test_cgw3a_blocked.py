"""Integration tests for codex-chatgpt-control adapter blocked behavior."""

import tempfile
from pathlib import Path

from chatgpt_visible_bridge.adapters import CodexChatGPTControlAdapter, get_adapter
from chatgpt_visible_bridge.schema import ResultStatus, Task, TaskStatus
from chatgpt_visible_bridge.telegram import TelegramRouter
from chatgpt_visible_bridge.workspace import Workspace
from chatgpt_visible_bridge.worker import Worker, process_one


def test_worker_with_codex_adapter_blocked():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        task = Task(prompt="请只回复 VISIBLE_CHATGPT_BRIDGE_OK")
        task.save(ws.task_path(task.id))

        adapter = get_adapter("codex-chatgpt-control")
        result = process_one(ws, adapter_name="codex-chatgpt-control")

        assert result is not None
        assert result.id == task.id
        assert result.status == ResultStatus.BLOCKED
        assert result.adapter == "codex-chatgpt-control"
        assert result.stop_reason == "browser_bridge_unavailable"
        assert "CGW-3A Skeleton" in result.summary
        assert "CGW-3B" in result.suggested_next_action

        # Task moved to failed/ (blocked tasks go to failed/)
        assert (ws.failed / f"{task.id}.json").exists()
        # Report written
        assert ws.report_path(task.id).exists()
        # Result written
        assert ws.result_path(task.id).exists()


def test_blocked_result_has_report_path():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        task = Task(prompt="Test")
        task.save(ws.task_path(task.id))

        adapter = CodexChatGPTControlAdapter()
        worker = Worker(ws, adapter)
        result = worker.process_one()

        assert result is not None
        assert result.report_path is not None
        assert Path(result.report_path).exists()
        # Report contains blocker info
        report = Path(result.report_path).read_text(encoding="utf-8")
        assert "blocked" in report.lower()
        assert "CGW-3A" in report
        assert "browser_bridge_unavailable" in report


def test_telegram_router_blocked_result():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            # Create task
            ask_response = router.route("/cgpt ask 请只回复 VISIBLE_CHATGPT_BRIDGE_OK")
            task_id = ask_response.split("ID:")[1].strip().split()[0].strip("`")

            # Process with codex adapter
            process_one(adapter_name="codex-chatgpt-control")

            # Query result via Telegram router
            result_response = router.route(f"/cgpt result {task_id}")

            assert "blocked" in result_response.lower()
            assert "codex-chatgpt-control" in result_response
            assert "CGW-3B" in result_response or "browser bridge" in result_response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_blocked_report_content():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        task = Task(prompt="请只回复 VISIBLE_CHATGPT_BRIDGE_OK")
        task.save(ws.task_path(task.id))

        adapter = CodexChatGPTControlAdapter()
        worker = Worker(ws, adapter)
        result = worker.process_one()

        assert result is not None
        report = ws.report_path(task.id).read_text(encoding="utf-8")
        assert result.status.value == "blocked"
        assert result.adapter == "codex-chatgpt-control"
        assert "CGW-3A Skeleton" in report
        assert "No real ChatGPT Web operation" in report
        assert "Next Phase" in report
        assert "CGW-3B" in report


def test_blocked_task_status_in_workspace():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        task = Task(prompt="Test")
        task.save(ws.task_path(task.id))

        process_one(ws, adapter_name="codex-chatgpt-control")

        # Task should be in failed/ directory with BLOCKED status
        failed_task = ws.failed_path(task.id)
        assert failed_task.exists()
        loaded = Task.load(failed_task)
        assert loaded.status == TaskStatus.BLOCKED


def test_cli_worker_once_with_codex_adapter():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            from chatgpt_visible_bridge.cli import main

            # Create task
            main(["create-task", "--prompt", "Test"])

            # Process with codex adapter
            ret = main(["worker-once", "--adapter", "codex-chatgpt-control"])
            assert ret == 0
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old
