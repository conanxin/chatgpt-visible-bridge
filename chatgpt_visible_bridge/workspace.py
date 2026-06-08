"""Workspace directory management for ChatGPT Visible Bridge."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

DEFAULT_CGW_HOME = Path.home() / ".openclaw" / "workspace" / "chatgpt-visible-bridge"


class Workspace:
    """Manages the runtime directories for the bridge."""

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or self._resolve_root()
        self.inbox = self.root / "inbox"
        self.active = self.root / "active"
        self.outbox = self.root / "outbox"
        self.failed = self.root / "failed"
        self.reports = self.root / "reports"
        self.logs = self.root / "logs"

    @staticmethod
    def _resolve_root() -> Path:
        env = os.getenv("CGW_HOME")
        if env:
            return Path(env).expanduser().resolve()
        return DEFAULT_CGW_HOME

    def ensure_dirs(self) -> None:
        """Create all runtime directories if they don't exist."""
        for d in (self.inbox, self.active, self.outbox, self.failed, self.reports, self.logs):
            d.mkdir(parents=True, exist_ok=True)

    def inbox_tasks(self) -> list[Path]:
        """Return sorted list of pending task files."""
        if not self.inbox.exists():
            return []
        return sorted(
            [p for p in self.inbox.iterdir() if p.suffix == ".json"],
            key=lambda p: p.stat().st_mtime,
        )

    def outbox_results(self) -> list[Path]:
        """Return sorted list of completed result files (excluding task records)."""
        if not self.outbox.exists():
            return []
        return sorted(
            [p for p in self.outbox.iterdir() if p.suffix == ".json" and not p.name.endswith("_task.json")],
            key=lambda p: p.stat().st_mtime,
        )

    def failed_tasks(self) -> list[Path]:
        """Return sorted list of failed task files."""
        if not self.failed.exists():
            return []
        return sorted(
            [p for p in self.failed.iterdir() if p.suffix == ".json"],
            key=lambda p: p.stat().st_mtime,
        )

    def active_task(self) -> Optional[Path]:
        """Return the active task file if one exists."""
        if not self.active.exists():
            return None
        tasks = [p for p in self.active.iterdir() if p.suffix == ".json"]
        return tasks[0] if tasks else None

    def report_path(self, task_id: str) -> Path:
        return self.reports / f"{task_id}.md"

    def result_path(self, task_id: str) -> Path:
        return self.outbox / f"{task_id}.json"

    def task_path(self, task_id: str) -> Path:
        return self.inbox / f"{task_id}.json"

    def active_path(self, task_id: str) -> Path:
        return self.active / f"{task_id}.json"

    def failed_path(self, task_id: str) -> Path:
        return self.failed / f"{task_id}.json"
