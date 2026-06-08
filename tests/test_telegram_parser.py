"""Tests for telegram/parser.py — command parsing."""

from chatgpt_visible_bridge.telegram.parser import (
    TelegramCommand,
    TelegramCommandType,
    parse_command,
)


def test_parse_ask():
    cmd = parse_command("/cgpt ask Review the architecture")
    assert cmd.type == TelegramCommandType.ASK
    assert cmd.prompt == "Review the architecture"
    assert cmd.error is None


def test_parse_ask_with_long_prompt():
    long_prompt = "Analyze this code: " + "x" * 10000
    cmd = parse_command(f"/cgpt ask {long_prompt}")
    assert cmd.type == TelegramCommandType.ASK
    assert cmd.prompt == long_prompt


def test_parse_ask_empty_prompt():
    cmd = parse_command("/cgpt ask")
    assert cmd.type == TelegramCommandType.UNKNOWN
    assert cmd.error is not None
    assert "Missing prompt" in cmd.error


def test_parse_status():
    cmd = parse_command("/cgpt status")
    assert cmd.type == TelegramCommandType.STATUS


def test_parse_result():
    cmd = parse_command("/cgpt result abc123")
    assert cmd.type == TelegramCommandType.RESULT
    assert cmd.task_id == "abc123"


def test_parse_result_missing_id():
    cmd = parse_command("/cgpt result")
    assert cmd.type == TelegramCommandType.UNKNOWN
    assert cmd.error is not None


def test_parse_show():
    cmd = parse_command("/cgpt show abc123")
    assert cmd.type == TelegramCommandType.SHOW
    assert cmd.task_id == "abc123"


def test_parse_show_missing_id():
    cmd = parse_command("/cgpt show")
    assert cmd.type == TelegramCommandType.UNKNOWN
    assert cmd.error is not None


def test_parse_help():
    cmd = parse_command("/cgpt help")
    assert cmd.type == TelegramCommandType.HELP


def test_parse_unknown_subcommand():
    cmd = parse_command("/cgpt delete abc123")
    assert cmd.type == TelegramCommandType.UNKNOWN
    assert cmd.error is not None
    assert "delete" in cmd.error


def test_parse_no_subcommand():
    cmd = parse_command("/cgpt")
    assert cmd.type == TelegramCommandType.UNKNOWN
    assert cmd.error is not None


def test_parse_not_cgpt_prefix():
    cmd = parse_command("hello world")
    assert cmd.type == TelegramCommandType.UNKNOWN
    assert cmd.error is not None
    assert "must start with" in cmd.error


def test_parse_result_multiple_args():
    cmd = parse_command("/cgpt result abc123 extra stuff")
    assert cmd.type == TelegramCommandType.RESULT
    assert cmd.task_id == "abc123"  # Only first token


def test_parse_show_multiple_args():
    cmd = parse_command("/cgpt show abc123 extra stuff")
    assert cmd.type == TelegramCommandType.SHOW
    assert cmd.task_id == "abc123"  # Only first token


def test_parse_whitespace_handling():
    cmd = parse_command("  /cgpt   ask   hello   ")
    assert cmd.type == TelegramCommandType.ASK
    assert cmd.prompt == "hello"


def test_parse_case_insensitive():
    cmd = parse_command("/CGPT ASK hello")
    # prefix must match exactly? Actually, let's check behavior
    # The current code uses exact startswith, so /CGPT won't match
    # This is fine, we just document the behavior
    assert cmd.type == TelegramCommandType.UNKNOWN


def test_parse_empty_after_prefix():
    cmd = parse_command("/cgpt ")
    assert cmd.type == TelegramCommandType.UNKNOWN
