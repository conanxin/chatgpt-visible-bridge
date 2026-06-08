"""Tests for cli.py — CLI smoke tests."""

import tempfile
from pathlib import Path

from chatgpt_visible_bridge.cli import main
from chatgpt_visible_bridge.workspace import Workspace


def test_cli_create_task(capsys):
    with tempfile.TemporaryDirectory() as tmp:
        ws = Workspace(root=Path(tmp))
        ws.ensure_dirs()
        # Use workspace override via env var simulation
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            ret = main(["create-task", "--prompt", "Test prompt"])
            assert ret == 0
            out = capsys.readouterr().out
            assert "Task created:" in out
            # Verify file exists
            assert len(ws.inbox_tasks()) == 1
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_cli_task_status_empty(capsys):
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            ret = main(["task-status"])
            assert ret == 0
            out = capsys.readouterr().out
            assert "Inbox (pending):" in out
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_cli_worker_once_mock(capsys):
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            # Create a task first
            main(["create-task", "--prompt", "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"])
            # Process it
            ret = main(["worker-once", "--mock"])
            assert ret == 0
            out = capsys.readouterr().out
            assert "Processed task:" in out
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_cli_task_result(capsys):
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            # Create a task
            main(["create-task", "--prompt", "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"])
            # Find the task ID from filesystem
            ws = Workspace(root=Path(tmp))
            task_id = ws.inbox_tasks()[0].stem
            # Process it
            main(["worker-once", "--mock"])
            # Query result
            ret = main(["task-result", task_id])
            assert ret == 0
            out = capsys.readouterr().out
            assert "Result JSON:" in out
            assert "VISIBLE_CHATGPT_BRIDGE_OK" in out
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_cli_task_show(capsys):
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            # Create task
            main(["create-task", "--prompt", "Hello world"])
            # Find task ID from filesystem
            ws = Workspace(root=Path(tmp))
            task_id = ws.inbox_tasks()[0].stem

            ret = main(["task-show", task_id])
            assert ret == 0
            out = capsys.readouterr().out
            assert "Task ID:" in out
            assert "Hello world" in out
            assert "Wrapped Prompt" in out
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old
