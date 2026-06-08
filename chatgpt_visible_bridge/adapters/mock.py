"""Mock adapter for ChatGPT Visible Bridge.

Returns structured responses without calling the network.
Default and safe for testing.
"""

from __future__ import annotations

from ..schema import Result, ResultStatus, Task
from .base import Adapter


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
