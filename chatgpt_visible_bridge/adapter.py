"""Adapter interface for ChatGPT Visible Bridge."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .schema import Result, ResultStatus, Task


class Adapter(ABC):
    """Base adapter for sending prompts to ChatGPT and receiving responses."""

    name: str = "base"

    @abstractmethod
    def send(self, task: Task) -> Result:
        """Process a task and return a result."""
        ...

    @property
    def available(self) -> bool:
        """Return whether this adapter is ready to use."""
        return True


class MockAdapter(Adapter):
    """Mock adapter that returns structured responses without calling ChatGPT."""

    name = "mock"

    def send(self, task: Task) -> Result:
        prompt = task.prompt.strip()

        # Special smoke-test prompt
        if prompt == "请只回复 VISIBLE_CHATGPT_BRIDGE_OK":
            return Result(
                id=task.id,
                status=ResultStatus.SUCCESS,
                summary="VISIBLE_CHATGPT_BRIDGE_OK",
                adapter=self.name,
                stop_reason="smoke_test_prompt",
                report_path=None,
            )

        # Standard mock response
        summary = (
            f"## 任务理解\n\n"
            f"已收到任务（ID: {task.id}）。以下是对请求的分析和建议。\n\n"
            f"## 建议\n\n"
            f"1. 仔细审查原始需求。\n"
            f"2. 将大任务拆分为可验证的小步骤。\n"
            f"3. 使用本地工具或脚本执行，而非自动执行。\n\n"
            f"## 风险点\n\n"
            f"- 自动执行未经审查的 AI 建议可能导致意外副作用。\n"
            f"- 文件操作前应确认路径和权限。\n"
            f"- 敏感信息不应离开本地环境。\n\n"
            f"## 下一步建议\n\n"
            f"- 在 `reports/` 中查看完整分析。\n"
            f"- 如需执行，请手动审核并运行 `/agent approve`。\n\n"
            f"---\n\n"
            f"**注意：这是 mock adapter，未调用真实 ChatGPT Web。**"
        )

        return Result(
            id=task.id,
            status=ResultStatus.SUCCESS,
            summary=summary,
            adapter=self.name,
            stop_reason="mock_consult_only",
            suggested_next_action="Review the report in reports/ and approve manually if needed.",
            report_path=None,
        )


class LiveAdapter(Adapter):
    """Placeholder for a real ChatGPT Web adapter.

    This adapter requires an external browser bridge (e.g., codex-chatgpt-control
    or a Playwright/Codex bridge) to interact with the ChatGPT Web interface.

    In the MVP, this adapter is intentionally blocked and returns a blocked result.
    """

    name = "live"

    @property
    def available(self) -> bool:
        return False

    def send(self, task: Task) -> Result:
        return Result(
            id=task.id,
            status=ResultStatus.BLOCKED,
            summary="Live adapter is not available in the MVP. "
                    "To use real ChatGPT Web, connect a browser bridge (e.g., codex-chatgpt-control). "
                    "See docs/WORKER_MODES.md for details.",
            adapter=self.name,
            stop_reason="browser_bridge_unavailable",
            suggested_next_action="Use --mock mode for testing, or connect a browser bridge for live mode.",
            report_path=None,
        )


def get_adapter(name: str) -> Adapter:
    """Factory to get an adapter by name."""
    adapters = {
        "mock": MockAdapter(),
        "live": LiveAdapter(),
    }
    if name not in adapters:
        raise ValueError(f"Unknown adapter: {name}. Available: {list(adapters.keys())}")
    return adapters[name]
