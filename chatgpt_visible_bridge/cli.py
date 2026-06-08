"""CLI entry point for ChatGPT Visible Bridge."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from . import __version__
from .adapters.codex_chatgpt_control import LIVE_ENV
from .adapter import get_adapter
from .schema import Task, TaskPolicy, TaskMode, TaskStatus, TaskType
from .telegram import TelegramRouter
from .workspace import Workspace
from .worker import drain, process_one

logger = logging.getLogger(__name__)


def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _workspace() -> Workspace:
    ws = Workspace()
    ws.ensure_dirs()
    return ws


def cmd_create_task(args: argparse.Namespace) -> int:
    ws = _workspace()
    task = Task(
        source=args.source or "cli",
        type=TaskType(args.type) if args.type else TaskType.GENERIC,
        prompt=args.prompt,
        mode=TaskMode(args.mode) if args.mode else TaskMode.CONSULT_ONLY,
        policy=TaskPolicy(
            consult_only=args.mode == "consult_only",
            allow_execute=args.allow_execute,
            allow_upload_files=args.allow_upload_files,
        ),
        reply_to=args.reply_to,
    )
    task_file = ws.task_path(task.id)
    task.save(task_file)
    print(f"Task created: {task.id}")
    print(f"  Path: {task_file}")
    return 0


def cmd_task_status(args: argparse.Namespace) -> int:
    ws = _workspace()
    inbox = ws.inbox_tasks()
    active = ws.active_task()
    outbox = ws.outbox_results()
    failed = ws.failed_tasks()

    print("ChatGPT Visible Bridge — Queue Status")
    print("=" * 40)
    print(f"  Inbox (pending):   {len(inbox)}")
    print(f"  Active:            {1 if active else 0}")
    print(f"  Outbox (completed): {len(outbox)}")
    print(f"  Failed:            {len(failed)}")
    print()

    if inbox and args.show:
        print("Recent pending tasks:")
        for p in inbox[-args.show:]:
            t = Task.load(p)
            print(f"  - {t.id} [{t.type.value}] {t.prompt[:60]}{'...' if len(t.prompt) > 60 else ''}")
        print()

    if active and args.show:
        t = Task.load(active)
        print(f"Active task: {t.id}")
        print(f"  Prompt: {t.prompt[:80]}{'...' if len(t.prompt) > 80 else ''}")
        print()

    return 0


def cmd_worker_once(args: argparse.Namespace) -> int:
    ws = _workspace()
    adapter = args.adapter or "mock"
    old_live = os.environ.get(LIVE_ENV)
    if args.live:
        os.environ[LIVE_ENV] = "1"
    try:
        result = process_one(ws, adapter_name=adapter)
    finally:
        if args.live:
            if old_live is None:
                os.environ.pop(LIVE_ENV, None)
            else:
                os.environ[LIVE_ENV] = old_live
    if result is None:
        print("No pending tasks.")
        return 0
    print(f"Processed task: {result.id}")
    print(f"  Status: {result.status.value}")
    print(f"  Adapter: {result.adapter}")
    if result.report_path:
        print(f"  Report: {result.report_path}")
    return 0


def cmd_worker_drain(args: argparse.Namespace) -> int:
    ws = _workspace()
    adapter = args.adapter or "mock"
    results = drain(ws, adapter_name=adapter)
    if not results:
        print("No pending tasks.")
        return 0
    print(f"Drained {len(results)} task(s):")
    for r in results:
        print(f"  - {r.id}: {r.status.value}")
    return 0


def cmd_task_result(args: argparse.Namespace) -> int:
    ws = _workspace()
    task_id = args.task_id
    result_path = ws.result_path(task_id)
    report_path = ws.report_path(task_id)

    if result_path.exists():
        data = json.loads(result_path.read_text(encoding="utf-8"))
        print("Result JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Result not found: {result_path}")

    if report_path.exists():
        print("\nReport Markdown:")
        print(report_path.read_text(encoding="utf-8"))
    else:
        print(f"Report not found: {report_path}")

    return 0


def cmd_task_show(args: argparse.Namespace) -> int:
    ws = _workspace()
    task_id = args.task_id

    # Search in inbox, active, failed, outbox
    candidates = [
        ws.task_path(task_id),
        ws.active_path(task_id),
        ws.failed_path(task_id),
    ]
    # Also check outbox for task records (named with _task suffix)
    candidates.append(ws.outbox / f"{task_id}_task.json")

    task_file = None
    for c in candidates:
        if c.exists():
            task_file = c
            break

    if not task_file:
        print(f"Task not found: {task_id}")
        return 1

    task = Task.load(task_file)
    print(f"Task ID: {task.id}")
    print(f"Status:  {task.status.value}")
    print(f"Source:  {task.source}")
    print(f"Type:    {task.type.value}")
    print(f"Mode:    {task.mode.value}")
    print(f"Policy:  consult_only={task.policy.consult_only}, allow_execute={task.policy.allow_execute}, allow_upload={task.policy.allow_upload_files}")
    print(f"Created: {task.created_at}")
    if task.reply_to:
        print(f"Reply to: {task.reply_to}")
    print()
    print("Original Prompt:")
    print("-" * 40)
    print(task.prompt)
    print()
    print("Wrapped Prompt (for ChatGPT):")
    print("-" * 40)
    wrapped = _wrap_prompt(task)
    print(wrapped)
    return 0


def _wrap_prompt(task: Task) -> str:
    """Build the wrapped prompt that would be sent to ChatGPT."""
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
    ]
    if task.policy.consult_only:
        lines.append(
            "This is a CONSULT-ONLY task. Please provide analysis and suggestions only. "
            "Do not generate executable commands or file operations unless explicitly allowed."
        )
    else:
        lines.append(
            "WARNING: EXECUTION MODE requested. This requires explicit user approval. "
            "Provide suggestions only; the user will review and approve manually."
        )
    return "\n".join(lines)


def cmd_telegram_router(args: argparse.Namespace) -> int:
    ws = _workspace()
    router = TelegramRouter(ws)
    response = router.route(args.message)
    print(response)
    return 0


def main(argv: list[str] | None = None) -> int:
    # Detect command from script name if no explicit subcommand provided
    invoked_name = Path(sys.argv[0]).name if sys.argv else "chatgpt-visible-bridge"
    command_map = {
        "cgpt-create-task": "create-task",
        "cgpt-task-status": "task-status",
        "cgpt-worker-once": "worker-once",
        "cgpt-worker-drain": "worker-drain",
        "cgpt-task-result": "task-result",
        "cgpt-task-show": "task-show",
        "cgpt-telegram-router": "telegram-router",
    }
    default_subcommand = command_map.get(invoked_name)

    # If argv is passed explicitly, use it; otherwise use sys.argv[1:]
    raw_argv = argv if argv is not None else sys.argv[1:]

    # If default subcommand exists and first arg is not a subcommand, prepend it
    if default_subcommand and raw_argv:
        # If the first arg is already a known subcommand, don't override
        known_subcommands = set(command_map.values())
        if raw_argv[0] not in known_subcommands and not raw_argv[0].startswith("-"):
            # Also check if it looks like a positional arg for task-result/task-show
            if default_subcommand in ("task-result", "task-show"):
                raw_argv = [default_subcommand, raw_argv[0]] + raw_argv[1:]
            else:
                raw_argv = [default_subcommand] + raw_argv
        elif raw_argv[0] not in known_subcommands and raw_argv[0].startswith("-"):
            raw_argv = [default_subcommand] + raw_argv
    elif default_subcommand and not raw_argv:
        raw_argv = [default_subcommand]

    parser = argparse.ArgumentParser(
        prog=invoked_name,
        description="ChatGPT Visible Bridge — manual, auditable, one-shot worker",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--log-level", default="INFO", help="Logging level (default: INFO)")
    sub = parser.add_subparsers(dest="command", required=True)

    # cgpt-create-task
    p_create = sub.add_parser("create-task", help="Create a task in inbox")
    p_create.add_argument("--prompt", required=True, help="Task prompt")
    p_create.add_argument("--source", default="cli", help="Task source")
    p_create.add_argument("--type", default="generic", choices=[t.value for t in TaskType], help="Task type")
    p_create.add_argument("--mode", default="consult_only", choices=["consult_only", "execute"], help="Task mode")
    p_create.add_argument("--allow-execute", action="store_true", help="Allow execution policy")
    p_create.add_argument("--allow-upload-files", action="store_true", help="Allow file upload policy")
    p_create.add_argument("--reply-to", help="Optional reply-to reference")
    p_create.set_defaults(func=cmd_create_task)

    # cgpt-task-status
    p_status = sub.add_parser("task-status", help="Show queue status")
    p_status.add_argument("--show", type=int, default=3, help="Show N recent tasks")
    p_status.set_defaults(func=cmd_task_status)

    # cgpt-worker-once
    p_once = sub.add_parser("worker-once", help="Process one task, then exit")
    p_once.add_argument("--adapter", default="mock", help="Adapter name (mock or codex-chatgpt-control)")
    p_once.add_argument("--mock", action="store_const", const="mock", dest="adapter", help="Use mock adapter")
    p_once.add_argument(
        "--live",
        action="store_true",
        help="Explicitly enable one-shot live mode for codex-chatgpt-control",
    )
    p_once.set_defaults(func=cmd_worker_once)

    # cgpt-worker-drain
    p_drain = sub.add_parser("worker-drain", help="Process all pending tasks, then exit")
    p_drain.add_argument("--adapter", default="mock", help="Adapter name (mock or codex-chatgpt-control)")
    p_drain.add_argument("--mock", action="store_const", const="mock", dest="adapter", help="Use mock adapter")
    p_drain.set_defaults(func=cmd_worker_drain)

    # cgpt-task-result
    p_result = sub.add_parser("task-result", help="Show result and report for a task")
    p_result.add_argument("task_id", help="Task ID")
    p_result.set_defaults(func=cmd_task_result)

    # cgpt-task-show
    p_show = sub.add_parser("task-show", help="Show raw and wrapped prompt for a task")
    p_show.add_argument("task_id", help="Task ID")
    p_show.set_defaults(func=cmd_task_show)

    # cgpt-telegram-router (developer helper)
    p_telegram = sub.add_parser("telegram-router", help="Simulate Telegram message routing (developer helper)")
    p_telegram.add_argument("message", help="Telegram message text to simulate")
    p_telegram.set_defaults(func=cmd_telegram_router)

    args = parser.parse_args(raw_argv)
    _setup_logging(args.log_level)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
