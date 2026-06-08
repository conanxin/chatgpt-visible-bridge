"""Tests for schema.py — Task and Result serialization."""

import json
import tempfile
from pathlib import Path

from chatgpt_visible_bridge.schema import (
    Result,
    ResultStatus,
    Task,
    TaskPolicy,
    TaskStatus,
    TaskType,
)


def test_task_defaults():
    t = Task()
    assert t.status == TaskStatus.PENDING
    assert t.mode.value == "consult_only"
    assert t.policy.consult_only is True
    assert len(t.id) == 16


def test_task_roundtrip():
    t = Task(
        source="cli",
        type=TaskType.ANALYSIS,
        prompt="Test prompt",
        policy=TaskPolicy(allow_execute=True),
        reply_to="12345",
    )
    data = t.to_dict()
    t2 = Task.from_dict(data)
    assert t2.source == "cli"
    assert t2.type == TaskType.ANALYSIS
    assert t2.prompt == "Test prompt"
    assert t2.policy.allow_execute is True
    assert t2.reply_to == "12345"


def test_task_save_load():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "task.json"
        t = Task(prompt="Hello")
        t.save(path)
        t2 = Task.load(path)
        assert t2.prompt == "Hello"
        assert t2.id == t.id


def test_result_defaults():
    r = Result(id="abc123", status=ResultStatus.SUCCESS, summary="Done")
    assert r.adapter == "mock"
    assert r.report_path is None


def test_result_roundtrip():
    r = Result(
        id="abc123",
        status=ResultStatus.SUCCESS,
        summary="Done",
        report_path="/tmp/report.md",
        stop_reason="done",
        suggested_next_action="next",
    )
    data = r.to_dict()
    r2 = Result.from_dict(data)
    assert r2.summary == "Done"
    assert r2.report_path == "/tmp/report.md"
    assert r2.stop_reason == "done"
    assert r2.suggested_next_action == "next"


def test_result_save_load():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "result.json"
        r = Result(id="abc", status=ResultStatus.SUCCESS, summary="OK")
        r.save(path)
        r2 = Result.load(path)
        assert r2.summary == "OK"


def test_task_policy_defaults():
    p = TaskPolicy()
    assert p.consult_only is True
    assert p.allow_execute is False
    assert p.allow_upload_files is False


def test_task_policy_from_dict():
    p = TaskPolicy.from_dict({"allow_execute": True})
    assert p.consult_only is True  # default
    assert p.allow_execute is True
