from __future__ import annotations

import json
from dataclasses import dataclass, field

AUTO_TOOLS = frozenset({"read_file", "list_dir", "glob_files", "search_code"})
CONFIRM_TOOLS = frozenset({"write_file", "edit_file", "run_shell"})


def requires_confirmation(tool_name: str) -> bool:
    return tool_name in CONFIRM_TOOLS


def allowlist_key(tool_name: str, arguments: str) -> tuple[str, str] | None:
    if not requires_confirmation(tool_name):
        return None
    try:
        args = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError:
        return (tool_name, arguments or "")
    if tool_name == "write_file":
        path = args.get("path")
        if not path:
            return (tool_name, "")
        return (tool_name, str(path))
    if tool_name == "edit_file":
        path = args.get("path")
        if not path:
            return (tool_name, "")
        return (tool_name, str(path))
    if tool_name == "run_shell":
        command = args.get("command")
        if command is None:
            return (tool_name, "")
        return (tool_name, str(command))
    return (tool_name, arguments or "")


@dataclass
class OperationAllowlist:
    _entries: set[tuple[str, str]] = field(default_factory=set)

    def is_allowed(self, tool_name: str, arguments: str) -> bool:
        key = allowlist_key(tool_name, arguments)
        if key is None:
            return True
        return key in self._entries

    def approve(self, tool_name: str, arguments: str) -> None:
        key = allowlist_key(tool_name, arguments)
        if key is not None:
            self._entries.add(key)

    def clear(self) -> None:
        self._entries.clear()

    def entries(self) -> list[list[str]]:
        return [[tool_name, key] for tool_name, key in sorted(self._entries)]

    @classmethod
    def from_entries(cls, entries: list[list[str]] | None) -> OperationAllowlist:
        allowlist = cls()
        for item in entries or []:
            if len(item) == 2:
                allowlist._entries.add((str(item[0]), str(item[1])))
        return allowlist
