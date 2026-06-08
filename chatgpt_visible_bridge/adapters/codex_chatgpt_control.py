"""Codex ChatGPT Control adapter for ChatGPT Visible Bridge.

The adapter is conservative by default. It only attempts a real ChatGPT Web
operation when live mode is explicitly enabled. Ordinary shells, CI, and test
runs keep returning a structured blocked result.
"""

from __future__ import annotations

import importlib
import inspect
import os
from collections.abc import Callable
from typing import Any

from ..schema import Result, ResultStatus, Task
from .base import Adapter

LIVE_ENV = "CGW_ENABLE_CODEX_CHATGPT_CONTROL_LIVE"


class CodexChatGPTControlAdapter(Adapter):
    """Guarded live adapter for codex-chatgpt-control browser bridge."""

    name = "codex-chatgpt-control"

    @property
    def available(self) -> bool:
        """Return whether live mode is explicitly enabled.

        This does not prove the browser bridge is reachable. The actual bridge
        check happens during ``send()`` so failures can be written as results.
        """
        return self._live_enabled()

    def send(self, task: Task) -> Result:
        """Send a task to ChatGPT Web through codex-chatgpt-control if enabled."""

        # Optional dry-run flag for testing the skeleton path without
        # changing the core behavior.
        dry_run = os.getenv("CGW_LIVE_ADAPTER_DRY_RUN", "0") == "1"
        if dry_run:
            return self._dry_run_result(task)

        if not self._live_enabled():
            return self._blocked_result(
                task,
                stop_reason="live_not_enabled",
                summary=(
                    "Live mode is not enabled. No real ChatGPT Web operation "
                    "was attempted."
                ),
                next_action=(
                    "Run one-shot live smoke from a compatible Codex/browser "
                    f"bridge host with {LIVE_ENV}=1 and worker-once --live."
                ),
            )

        try:
            control = importlib.import_module("codex_chatgpt_control")
        except ImportError:
            return self._blocked_result(
                task,
                stop_reason="dependency_missing",
                summary=(
                    "The Python package `codex_chatgpt_control` is not "
                    "installed in this runtime."
                ),
                next_action=(
                    "Install or expose the documented codex-chatgpt-control "
                    "Python package in this Codex/browser bridge host, then "
                    "rerun worker-once --adapter codex-chatgpt-control --live."
                ),
            )

        try:
            response_markdown = self._send_via_control_package(control, task)
        except LiveAdapterBlocked as exc:
            return self._blocked_result(
                task,
                stop_reason=exc.stop_reason,
                summary=exc.summary,
                next_action=exc.next_action,
            )
        except Exception as exc:
            return self._blocked_result(
                task,
                stop_reason="browser_bridge_unavailable",
                summary=(
                    "codex-chatgpt-control could not complete the live "
                    f"browser operation: {type(exc).__name__}: {exc}"
                ),
                next_action=(
                    "Confirm ChatGPT is logged in and a compatible visible "
                    "browser bridge is available, then rerun the one-shot live smoke."
                ),
            )

        summary = self._summarize_response(response_markdown)
        return Result(
            id=task.id,
            status=ResultStatus.SUCCESS,
            summary=summary,
            adapter=self.name,
            stop_reason=None,
            suggested_next_action=None,
            report_path=None,
            response_markdown=response_markdown,
        )

    def _live_enabled(self) -> bool:
        return os.getenv(LIVE_ENV, "0") == "1"

    def _blocked_result(
        self,
        task: Task,
        *,
        stop_reason: str,
        summary: str,
        next_action: str,
    ) -> Result:
        summary = (
            "## CGW-3B Live Adapter Blocked\n\n"
            "**No real ChatGPT Web operation was attempted.**\n\n"
            "### Blocker Details\n\n"
            "- **Status:** blocked\n"
            f"- **Stop Reason:** {stop_reason}\n"
            "- **Adapter:** codex-chatgpt-control\n\n"
            "### Summary\n\n"
            f"{summary}\n\n"
            "### Next Safe Action\n\n"
            f"{next_action}\n\n"
            "---\n\n"
            "_CGW-3B: safe blocked fallback, no upload/download, no cookie/session access._"
        )

        return Result(
            id=task.id,
            status=ResultStatus.BLOCKED,
            summary=summary,
            adapter=self.name,
            stop_reason=stop_reason,
            suggested_next_action=next_action,
            report_path=None,
        )

    def _send_via_control_package(self, control: Any, task: Task) -> str:
        prompt = self._wrap_prompt(task)

        callable_obj = self._find_control_callable(control)
        if callable_obj is None:
            raise LiveAdapterBlocked(
                stop_reason="dependency_missing",
                summary=(
                    "`codex_chatgpt_control` is importable, but no supported "
                    "documented prompt submission API was found."
                ),
                next_action=(
                    "Use a codex-chatgpt-control build that exposes one of "
                    "send_prompt, submit_prompt, ask, run, or a "
                    "ChatGPTControlClient with send_prompt/submit_prompt."
                ),
            )

        response = self._call_control_callable(callable_obj, prompt)
        response_markdown = self._extract_response_markdown(response)
        if not response_markdown:
            raise LiveAdapterBlocked(
                stop_reason="ui_state_unavailable",
                summary=(
                    "codex-chatgpt-control returned without readable Markdown "
                    "content from ChatGPT Web."
                ),
                next_action=(
                    "Confirm the visible ChatGPT page is usable and rerun the "
                    "one-shot live smoke."
                ),
            )
        return response_markdown

    def _find_control_callable(self, control: Any) -> Callable[..., Any] | None:
        for attr in ("send_prompt", "submit_prompt", "ask", "run"):
            candidate = getattr(control, attr, None)
            if callable(candidate):
                return candidate

        client_cls = getattr(control, "ChatGPTControlClient", None)
        if client_cls is not None:
            client = client_cls()
            for attr in ("send_prompt", "submit_prompt", "ask", "run"):
                candidate = getattr(client, attr, None)
                if callable(candidate):
                    return candidate
        return None

    def _call_control_callable(self, callable_obj: Callable[..., Any], prompt: str) -> Any:
        kwargs = {
            "prompt": prompt,
            "thread": "new",
            "thread_mode": "new",
            "response_format": "markdown",
            "upload_files": False,
            "download_files": False,
        }
        signature = inspect.signature(callable_obj)
        params = signature.parameters
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in params.values())
        filtered_kwargs = (
            kwargs
            if accepts_kwargs
            else {k: v for k, v in kwargs.items() if k in params}
        )
        if filtered_kwargs:
            return callable_obj(**filtered_kwargs)
        return callable_obj(prompt)

    def _extract_response_markdown(self, response: Any) -> str:
        if isinstance(response, str):
            return response.strip()
        if isinstance(response, dict):
            for key in ("response_markdown", "markdown", "content", "text", "response"):
                value = response.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            status = response.get("status")
            stop_reason = response.get("stop_reason") or response.get("reason")
            if status == "blocked" or stop_reason:
                raise LiveAdapterBlocked(
                    stop_reason=str(stop_reason or "browser_bridge_unavailable"),
                    summary=str(response.get("summary") or "Live browser bridge reported a blocker."),
                    next_action=str(
                        response.get("next_action")
                        or response.get("suggested_next_action")
                        or "Resolve the browser bridge blocker and rerun one-shot live smoke."
                    ),
                )
        for attr in ("response_markdown", "markdown", "content", "text", "response"):
            value = getattr(response, attr, None)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _wrap_prompt(self, task: Task) -> str:
        lines = [
            "[Task Queue Bridge]",
            f"Task ID: {task.id}",
            f"Mode: {task.mode.value}",
            f"Policy: consult_only={task.policy.consult_only}",
            "",
            "--- User Request ---",
            "",
            task.prompt,
            "",
            "--- System Note ---",
            "",
            "Return Markdown only. Do not execute local commands. Do not request "
            "file uploads or downloads.",
        ]
        return "\n".join(lines)

    def _summarize_response(self, response_markdown: str) -> str:
        compact = " ".join(response_markdown.split())
        return compact[:500] + ("..." if len(compact) > 500 else "")

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


class LiveAdapterBlocked(Exception):
    """Structured live adapter blocker."""

    def __init__(self, *, stop_reason: str, summary: str, next_action: str) -> None:
        super().__init__(summary)
        self.stop_reason = stop_reason
        self.summary = summary
        self.next_action = next_action
