"""Telegram message formatter for ChatGPT Visible Bridge.

Formats structured data into Telegram-friendly text.

Rules:
- No markdown tables (Discord/WhatsApp/Telegram don't render them well)
- Use bullet lists and emoji
- Keep responses concise but informative
- Truncate long content safely
"""

from __future__ import annotations

from typing import Optional

MAX_PROMPT_LENGTH = 4000  # Telegram message limit is ~4096 chars
TRUNCATE_SUFFIX = "\n... (truncated)"


def truncate(text: str, max_len: int = MAX_PROMPT_LENGTH, suffix: str = TRUNCATE_SUFFIX) -> str:
    """Truncate text to max_len, adding suffix if truncated."""
    if len(text) <= max_len:
        return text
    # Leave room for suffix
    return text[: max_len - len(suffix)] + suffix


def format_ask_response(task_id: str, status: str, prompt: str) -> str:
    """Format response for /cgpt ask."""
    safe_prompt = truncate(prompt, max_len=200)
    return (
        f"✅ Task created\n"
        f"\n"
        f"🆔 ID: `{task_id}`\n"
        f"📌 Status: {status}\n"
        f"\n"
        f"💬 Prompt: {safe_prompt}\n"
        f"\n"
        f"🖥️ Next step: run this in your terminal:\n"
        f"```\n"
        f"cgpt-worker-once --mock\n"
        f"```\n"
        f"\n"
        f"📖 Query result: /cgpt result {task_id}"
    )


def format_ask_error(error: str) -> str:
    """Format error response for /cgpt ask."""
    return f"❌ {error}\n\nType /cgpt help for usage."


def format_status(inbox: int, active: int, outbox: int, failed: int, recent_ids: list[str]) -> str:
    """Format response for /cgpt status."""
    lines = [
        "📊 Queue Status",
        "",
        f"• Inbox (pending): {inbox}",
        f"• Active: {active}",
        f"• Outbox (completed): {outbox}",
        f"• Failed: {failed}",
    ]
    if recent_ids:
        lines.append("")
        lines.append("📎 Recent tasks:")
        for tid in recent_ids[:5]:
            lines.append(f"  - `{tid}`")
    return "\n".join(lines)


def format_result(
    task_id: str,
    status: str,
    summary: str,
    adapter: str,
    report_path: Optional[str] = None,
    not_found: bool = False,
    pending: bool = False,
) -> str:
    """Format response for /cgpt result."""
    if not_found:
        return (
            f"🔍 Task `{task_id}` not found.\n"
            f"\n"
            f"Check status with /cgpt status\n"
            f"Or check the task ID is correct."
        )

    if pending:
        return (
            f"⏳ Task `{task_id}` is still {status}.\n"
            f"\n"
            f"Run this in your terminal to process:\n"
            f"```\n"
            f"cgpt-worker-once --mock\n"
            f"```"
        )

    safe_summary = truncate(summary, max_len=3000)
    lines = [
        f"📄 Result for `{task_id}`",
        "",
        f"✅ Status: {status}",
        f"🔌 Adapter: {adapter}",
        "",
        "📝 Summary:",
        safe_summary,
    ]
    if report_path:
        lines.append("")
        lines.append(f"📁 Report: `{report_path}`")
    return "\n".join(lines)


def format_show(
    task_id: str,
    status: str,
    prompt: str,
    mode: str,
    policy: dict,
    created_at: str,
    not_found: bool = False,
) -> str:
    """Format response for /cgpt show."""
    if not_found:
        return (
            f"🔍 Task `{task_id}` not found.\n"
            f"\n"
            f"Check status with /cgpt status."
        )

    safe_prompt = truncate(prompt, max_len=2000)
    lines = [
        f"🔍 Task `{task_id}`",
        "",
        f"📌 Status: {status}",
        f"🎯 Mode: {mode}",
        f"📅 Created: {created_at}",
        f"🔒 Policy: consult_only={policy.get('consult_only', True)}, "
        f"execute={policy.get('allow_execute', False)}, "
        f"upload={policy.get('allow_upload_files', False)}",
        "",
        "💬 Prompt:",
        "```",
        safe_prompt,
        "```",
    ]
    return "\n".join(lines)


def format_help() -> str:
    """Format response for /cgpt help."""
    return (
        "🤖 ChatGPT Visible Bridge — Telegram Commands\n"
        "\n"
        "📌 Usage:\n"
        "\n"
        "`/cgpt ask <prompt>` — Create a new task\n"
        "  Example: `/cgpt ask Review the architecture of this project`\n"
        "\n"
        "`/cgpt status` — Show queue status\n"
        "\n"
        "`/cgpt result <task_id>` — Show result and report\n"
        "  Example: `/cgpt result a1b2c3d4`\n"
        "\n"
        "`/cgpt show <task_id>` — Show task details and prompt\n"
        "  Example: `/cgpt show a1b2c3d4`\n"
        "\n"
        "`/cgpt help` — Show this message\n"
        "\n"
        "⚠️ All tasks are consult-only by default.\n"
        "No automatic execution."
    )


def format_unknown(error: str) -> str:
    """Format response for unknown command."""
    return (
        f"❓ Unknown command\n"
        f"\n"
        f"{error}\n"
        f"\n"
        f"Type /cgpt help for usage."
    )
