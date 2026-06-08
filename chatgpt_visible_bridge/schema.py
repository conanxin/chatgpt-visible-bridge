"""Core schema for ChatGPT Visible Bridge task and result contracts."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskType(str, Enum):
    CHAT = "chat"
    ANALYSIS = "analysis"
    CODE_REVIEW = "code_review"
    PLANNING = "planning"
    GENERIC = "generic"


class TaskMode(str, Enum):
    CONSULT_ONLY = "consult_only"
    EXECUTE = "execute"


class WorkerMode(str, Enum):
    MOCK = "mock"
    LIVE = "live"


class ResultStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TaskPolicy:
    consult_only: bool = True
    allow_execute: bool = False
    allow_upload_files: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TaskPolicy":
        return cls(
            consult_only=d.get("consult_only", True),
            allow_execute=d.get("allow_execute", False),
            allow_upload_files=d.get("allow_upload_files", False),
        )


@dataclass
class Task:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    source: str = "cli"
    type: TaskType = TaskType.GENERIC
    status: TaskStatus = TaskStatus.PENDING
    prompt: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    mode: TaskMode = TaskMode.CONSULT_ONLY
    policy: TaskPolicy = field(default_factory=TaskPolicy)
    reply_to: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "type": self.type.value,
            "status": self.status.value,
            "prompt": self.prompt,
            "created_at": self.created_at,
            "mode": self.mode.value,
            "policy": self.policy.to_dict(),
            "reply_to": self.reply_to,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Task":
        return cls(
            id=d.get("id", uuid.uuid4().hex[:16]),
            source=d.get("source", "cli"),
            type=TaskType(d.get("type", "generic")),
            status=TaskStatus(d.get("status", "pending")),
            prompt=d.get("prompt", ""),
            created_at=d.get("created_at", datetime.now(timezone.utc).isoformat()),
            mode=TaskMode(d.get("mode", "consult_only")),
            policy=TaskPolicy.from_dict(d.get("policy", {})),
            reply_to=d.get("reply_to"),
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: Path) -> None:
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Task":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


@dataclass
class Result:
    id: str
    status: ResultStatus
    summary: str
    report_path: Optional[str] = None
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    adapter: str = "mock"
    stop_reason: Optional[str] = None
    suggested_next_action: Optional[str] = None
    response_markdown: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status.value,
            "summary": self.summary,
            "report_path": self.report_path,
            "completed_at": self.completed_at,
            "adapter": self.adapter,
            "stop_reason": self.stop_reason,
            "suggested_next_action": self.suggested_next_action,
            "response_markdown": self.response_markdown,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: Path) -> None:
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Result":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Result":
        return cls(
            id=d["id"],
            status=ResultStatus(d.get("status", "success")),
            summary=d.get("summary", ""),
            report_path=d.get("report_path"),
            completed_at=d.get("completed_at", datetime.now(timezone.utc).isoformat()),
            adapter=d.get("adapter", "mock"),
            stop_reason=d.get("stop_reason"),
            suggested_next_action=d.get("suggested_next_action"),
            response_markdown=d.get("response_markdown"),
        )
