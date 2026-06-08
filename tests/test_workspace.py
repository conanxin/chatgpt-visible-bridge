"""Tests for workspace.py — directory creation and file management."""

import tempfile
from pathlib import Path

from chatgpt_visible_bridge.workspace import Workspace


def test_ensure_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        assert ws.inbox.exists()
        assert ws.active.exists()
        assert ws.outbox.exists()
        assert ws.failed.exists()
        assert ws.reports.exists()
        assert ws.logs.exists()


def test_inbox_tasks_empty():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        assert ws.inbox_tasks() == []


def test_inbox_tasks_sorted():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        # Create two tasks with different mtimes
        (ws.inbox / "task1.json").write_text("{}")
        (ws.inbox / "task2.json").write_text("{}")
        tasks = ws.inbox_tasks()
        assert len(tasks) == 2
        assert all(p.suffix == ".json" for p in tasks)


def test_active_task():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        assert ws.active_task() is None
        (ws.active / "task.json").write_text("{}")
        assert ws.active_task() is not None


def test_paths():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        assert ws.report_path("abc") == ws.reports / "abc.md"
        assert ws.result_path("abc") == ws.outbox / "abc.json"
        assert ws.task_path("abc") == ws.inbox / "abc.json"
