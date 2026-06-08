"""Tests for worker.py — claim, process, result, fail."""

import tempfile
from pathlib import Path

from chatgpt_visible_bridge.adapter import MockAdapter
from chatgpt_visible_bridge.schema import ResultStatus, Task, TaskStatus
from chatgpt_visible_bridge.workspace import Workspace
from chatgpt_visible_bridge.worker import Worker, process_one


def test_process_one_smoke_prompt():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        task = Task(prompt="请只回复 VISIBLE_CHATGPT_BRIDGE_OK")
        task.save(ws.task_path(task.id))

        result = process_one(ws, adapter_name="mock")
        assert result is not None
        assert result.id == task.id
        assert result.status == ResultStatus.SUCCESS
        assert "VISIBLE_CHATGPT_BRIDGE_OK" in result.summary
        assert result.adapter == "mock"

        # Check task moved to outbox
        assert ws.task_path(task.id).exists() is False
        assert (ws.outbox / f"{task.id}_task.json").exists()
        # Check report written
        assert ws.report_path(task.id).exists()
        # Check result written
        assert ws.result_path(task.id).exists()


def test_process_one_generic_prompt():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        task = Task(prompt="What is the best architecture for a task queue?")
        task.save(ws.task_path(task.id))

        result = process_one(ws, adapter_name="mock")
        assert result is not None
        assert result.status == ResultStatus.SUCCESS
        assert "mock adapter" in result.summary
        assert result.stop_reason == "mock_consult_only"


def test_process_one_no_pending():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        result = process_one(ws, adapter_name="mock")
        assert result is None


def test_drain():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        for i in range(3):
            task = Task(prompt=f"Task {i}")
            task.save(ws.task_path(task.id))

        from chatgpt_visible_bridge.worker import drain
        results = drain(ws, adapter_name="mock")
        assert len(results) == 3
        assert ws.inbox_tasks() == []
        assert len(ws.outbox_results()) == 3


def test_worker_exception_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        task = Task(prompt="test")
        task.save(ws.task_path(task.id))

        class BadAdapter:
            name = "bad"

            def send(self, task):
                raise RuntimeError("boom")

        worker = Worker(ws, BadAdapter())  # type: ignore
        result = worker.process_one()
        assert result is not None
        assert result.status == ResultStatus.FAILED
        assert "boom" in result.summary
        assert (ws.failed / f"{task.id}.json").exists()


def test_report_written():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        task = Task(prompt="请只回复 VISIBLE_CHATGPT_BRIDGE_OK")
        task.save(ws.task_path(task.id))

        process_one(ws, adapter_name="mock")
        report = ws.report_path(task.id).read_text(encoding="utf-8")
        assert "ChatGPT Visible Bridge Report" in report
        assert task.prompt in report
        assert "VISIBLE_CHATGPT_BRIDGE_OK" in report
