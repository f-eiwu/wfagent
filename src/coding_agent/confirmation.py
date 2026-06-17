import json
import sys
from collections.abc import Callable

from coding_agent.operation_allowlist import OperationAllowlist, requires_confirmation

ApprovalPrompt = Callable[[str], bool]


def format_prompt_summary(tool_name: str, arguments: str) -> str:
    try:
        args = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError:
        return tool_name
    if tool_name == "write_file":
        return f"write_file path={args.get('path', '?')}"
    if tool_name == "edit_file":
        return f"edit_file path={args.get('path', '?')}"
    if tool_name == "run_shell":
        return f"run_shell command={args.get('command', '?')}"
    return tool_name


def require_approval(
    tool_name: str,
    arguments: str,
    allowlist: OperationAllowlist,
    prompt_fn: ApprovalPrompt | None = None,
    *,
    auto_approve: bool = False,
) -> tuple[bool, str]:
    if not requires_confirmation(tool_name):
        return True, ""
    if auto_approve:
        return True, ""
    if allowlist.is_allowed(tool_name, arguments):
        return True, ""
    summary = format_prompt_summary(tool_name, arguments)
    if prompt_fn is not None:
        if prompt_fn(summary):
            allowlist.approve(tool_name, arguments)
            return True, ""
        return False, f"Error: user rejected {summary}"
    if not sys.stdin.isatty():
        return False, "Error: confirmation required for risky action (run interactively)"
    try:
        response = input(f"Approve {summary}? [y/N] ").strip().lower()
    except EOFError:
        return False, f"Error: user rejected {summary}"
    if response in ("y", "yes"):
        allowlist.approve(tool_name, arguments)
        return True, ""
    return False, f"Error: user rejected {summary}"
