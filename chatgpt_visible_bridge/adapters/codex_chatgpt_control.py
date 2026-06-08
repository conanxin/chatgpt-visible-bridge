"""Codex ChatGPT Control adapter skeleton for ChatGPT Visible Bridge.

This is a CGW-3A skeleton adapter. It does NOT call the real ChatGPT Web
or browser bridge. It returns a blocked result by default, indicating that
the live browser bridge is unavailable outside a compatible browser host.

Real live smoke will be implemented in CGW-3B from a compatible browser
bridge host (e.g., Codex Desktop).
"""

from __future__ import annotations

import os

from ..schema import Result, ResultStatus, Task
from .base import Adapter


class CodexChatGPTControlAdapter(Adapter):
    """Skeleton adapter for codex-chatgpt-control browser bridge.

    CGW-3A behavior: Returns blocked by default. The real browser bridge
    requires a compatible browser host (e.g., Codex Desktop) which is not
    available in this development environment.

    CGW-3B will implement the actual bridge communication via:
    - IPC (stdin/stdout) to codex-chatgpt-control CLI
    - HTTP to a local browser bridge service
    - File exchange with the bridge process
    """

    name = "codex-chatgpt-control"

    @property
    def available(self) -> bool:
        """The skeleton is never available in CGW-3A."""
        return False

    def send(self, task: Task) -> Result:
        """Return a blocked result explaining the CGW-3A skeleton status."""

        # Optional dry-run flag for testing the skeleton path without
        # changing the core behavior.
        dry_run = os.getenv("CGW_LIVE_ADAPTER_DRY_RUN", "0") == "1"
        if dry_run:
            return self._dry_run_result(task)

        return self._blocked_result(task)

    def _blocked_result(self, task: Task) -> Result:
        summary = (
            "## CGW-3A Skeleton Status\n\n"
            "This is the `codex-chatgpt-control` adapter skeleton.\n\n"
            "**No real ChatGPT Web operation was attempted.**\n\n"
            "The browser bridge is not available in this environment. "
            "A real browser bridge requires a compatible host with a live browser "
            "(e.g., Codex Desktop or a local Playwright bridge).\n\n"
            "### Blocker Details\n\n"
            "- **Status:** blocked\n"
            "- **Stop Reason:** browser_bridge_unavailable\n"
            "- **Adapter:** codex-chatgpt-control\n\n"
            "### Next Phase\n\n"
            "Run **CGW-3B** from a compatible browser bridge host to enable live ChatGPT Web interaction.\n\n"
            "---\n\n"
            "_CGW-3A: safe skeleton, no network calls, no browser automation._"
        )

        return Result(
            id=task.id,
            status=ResultStatus.BLOCKED,
            summary=summary,
            adapter=self.name,
            stop_reason="browser_bridge_unavailable",
            suggested_next_action=(
                "Run CGW-3B from a compatible browser bridge host "
                "(e.g., Codex Desktop) to enable live ChatGPT Web interaction."
            ),
            report_path=None,
        )

    def _dry_run_result(self, task: Task) -> Result:
        summary = (
            "## CGW-3A Dry-Run\n\n"
            "`CGW_LIVE_ADAPTER_DRY_RUN=1` is set.\n\n"
            "This is a dry-run of the `codex-chatgpt-control` adapter path. "
            "No real ChatGPT Web operation was attempted.\n\n"
            "In a real CGW-3B environment, the adapter would:\n"
            "1. Launch a browser bridge (e.g., codex-chatgpt-control).\n"
            "2. Send the wrapped prompt to the ChatGPT Web interface.\n"
            "3. Wait for the response.\n"
            "4. Return the actual ChatGPT response.\n\n"
            "---\n\n"
            "_CGW-3A dry-run: no network calls, no browser automation._"
        )

        return Result(
            id=task.id,
            status=ResultStatus.BLOCKED,
            summary=summary,
            adapter=self.name,
            stop_reason="browser_bridge_unavailable",
            suggested_next_action="Run CGW-3B from a compatible browser bridge host.",
            report_path=None,
        )
