"""Integration tests for telegram/handler.py using temp CGW_HOME.

These tests verify that the Telegram handler correctly interacts with the
file-based task queue without touching the real workspace.
"""

import tempfile
from pathlib import Path

from chatgpt_visible_bridge.telegram import TelegramRouter
from chatgpt_visible_bridge.worker import process_one


def test_handle_ask_creates_task():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            response = router.route("/cgpt ask 请只回复 VISIBLE_CHATGPT_BRIDGE_OK")

            assert "✅ Task created" in response
            assert "ID:" in response
            assert "Status: pending" in response
            assert "cgpt-worker-once" in response
            assert "/cgpt result" in response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_handle_status_empty():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            response = router.route("/cgpt status")

            assert "📊 Queue Status" in response
            assert "Inbox (pending): 0" in response
            assert "Active: 0" in response
            assert "Outbox (completed): 0" in response
            assert "Failed: 0" in response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_handle_status_with_pending():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            # Create a task first
            router.route("/cgpt ask Test task")
            # Check status
            response = router.route("/cgpt status")

            assert "Inbox (pending): 1" in response
            assert "Recent tasks:" in response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_handle_ask_then_worker_then_result():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            # Create task
            ask_response = router.route("/cgpt ask 请只回复 VISIBLE_CHATGPT_BRIDGE_OK")
            # Extract task ID from response
            task_id = ask_response.split("ID:")[1].strip().split()[0].strip("`")

            # Process with worker
            process_one(adapter_name="mock")

            # Query result
            result_response = router.route(f"/cgpt result {task_id}")

            assert "Result for" in result_response
            assert "VISIBLE_CHATGPT_BRIDGE_OK" in result_response
            assert "success" in result_response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_handle_result_pending():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            # Create task but don't process
            ask_response = router.route("/cgpt ask Test pending task")
            task_id = ask_response.split("ID:")[1].strip().split()[0].strip("`")

            # Query result without processing
            result_response = router.route(f"/cgpt result {task_id}")

            assert "still pending" in result_response
            assert "cgpt-worker-once" in result_response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_handle_result_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            response = router.route("/cgpt result nonexistent123")

            assert "not found" in response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_handle_show():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            # Create task
            ask_response = router.route("/cgpt ask Hello world")
            task_id = ask_response.split("ID:")[1].strip().split()[0].strip("`")

            # Show task
            show_response = router.route(f"/cgpt show {task_id}")

            assert "Task" in show_response
            assert "Hello world" in show_response
            assert "consult_only" in show_response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_handle_show_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            response = router.route("/cgpt show nonexistent123")

            assert "not found" in response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_handle_help():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            response = router.route("/cgpt help")

            assert "ChatGPT Visible Bridge" in response
            assert "/cgpt ask" in response
            assert "/cgpt status" in response
            assert "/cgpt result" in response
            assert "/cgpt show" in response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_handle_unknown():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            response = router.route("/cgpt delete abc123")

            assert "Unknown" in response or "Unknown command" in response
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old


def test_handle_empty_ask():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.environ.get("CGW_HOME")
        os.environ["CGW_HOME"] = str(tmp)
        try:
            router = TelegramRouter()
            response = router.route("/cgpt ask")

            assert "Missing" in response or "help" in response.lower()
        finally:
            if old is None:
                os.environ.pop("CGW_HOME", None)
            else:
                os.environ["CGW_HOME"] = old
