"""Telegram command handler for ChatGPT Visible Bridge.

Connects parsed Telegram commands to the underlying task queue logic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..schema import Task, TaskPolicy, TaskStatus, TaskType
from ..workspace import Workspace
from ..worker import process_one
from .formatter import (
    format_ask_error,
    format_ask_response,
    format_help,
    format_result,
    format_show,
    format_status,
    format_unknown,
)
from .parser import TelegramCommand, TelegramCommandType


class TelegramHandler:
    """Handles Telegram commands by interacting with the local task queue."""

    def __init__(self, workspace: Optional[Workspace] = None) -> None:
        self.workspace = workspace or Workspace()
        self.workspace.ensure_dirs()

    def handle(self, command: TelegramCommand) -> str:
        """Dispatch a parsed command to the appropriate handler."""
        if command.type == TelegramCommandType.ASK:
            return self._handle_ask(command)
        elif command.type == TelegramCommandType.STATUS:
            return self._handle_status()
        elif command.type == TelegramCommandType.RESULT:
            return self._handle_result(command)
        elif command.type == TelegramCommandType.SHOW:
            return self._handle_show(command)
        elif command.type == TelegramCommandType.HELP:
            return format_help()
        elif command.type == TelegramCommandType.UNKNOWN:
            return format_unknown(command.error or "Unrecognized command")
        else:
            return format_unknown("Unhandled command type")

    def _handle_ask(self, command: TelegramCommand) -> str:
        if not command.prompt:
            return format_ask_error("Missing prompt. Usage: /cgpt ask <prompt>")

        task = Task(
            source="telegram",
            type=TaskType.GENERIC,
            prompt=command.prompt,
            policy=TaskPolicy(
                consult_only=True,
                allow_execute=False,
                allow_upload_files=False,
            ),
        )
        task_file = self.workspace.task_path(task.id)
        task.save(task_file)
        return format_ask_response(
            task_id=task.id,
            status=task.status.value,
            prompt=task.prompt,
        )

    def _handle_status(self) -> str:
        inbox = self.workspace.inbox_tasks()
        active = self.workspace.active_task()
        outbox = self.workspace.outbox_results()
        failed = self.workspace.failed_tasks()

        recent_ids = [p.stem for p in inbox[-3:]]
        return format_status(
            inbox=len(inbox),
            active=1 if active else 0,
            outbox=len(outbox),
            failed=len(failed),
            recent_ids=recent_ids,
        )

    def _handle_result(self, command: TelegramCommand) -> str:
        if not command.task_id:
            return format_unknown("Missing task_id. Usage: /cgpt result <task_id>")

        result_path = self.workspace.result_path(command.task_id)
        if result_path.exists():
            data = json.loads(result_path.read_text(encoding="utf-8"))
            return format_result(
                task_id=command.task_id,
                status=data.get("status", "unknown"),
                summary=data.get("summary", ""),
                adapter=data.get("adapter", "unknown"),
                report_path=data.get("report_path"),
            )

        # Check if task is still pending/active
        candidates = [
            self.workspace.task_path(command.task_id),
            self.workspace.active_path(command.task_id),
        ]
        for c in candidates:
            if c.exists():
                task = Task.load(c)
                return format_result(
                    task_id=command.task_id,
                    status=task.status.value,
                    summary="",
                    adapter="",
                    report_path=None,
                    pending=True,
                )

        return format_result(
            task_id=command.task_id,
            status="unknown",
            summary="",
            adapter="",
            report_path=None,
            not_found=True,
        )

    def _handle_show(self, command: TelegramCommand) -> str:
        if not command.task_id:
            return format_unknown("Missing task_id. Usage: /cgpt show <task_id>")

        candidates = [
            self.workspace.task_path(command.task_id),
            self.workspace.active_path(command.task_id),
            self.workspace.failed_path(command.task_id),
            self.workspace.outbox / f"{command.task_id}_task.json",
        ]

        for c in candidates:
            if c.exists():
                task = Task.load(c)
                return format_show(
                    task_id=task.id,
                    status=task.status.value,
                    prompt=task.prompt,
                    mode=task.mode.value,
                    policy=task.policy.to_dict(),
                    created_at=task.created_at,
                )

        return format_show(
            task_id=command.task_id,
            status="unknown",
            prompt="",
            mode="unknown",
            policy={},
            created_at="",
            not_found=True,
        )
