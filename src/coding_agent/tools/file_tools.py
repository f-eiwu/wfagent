from pathlib import Path
import re

from coding_agent.security.path_policy import resolve_safe_path
from coding_agent.security.redaction import redact_secrets
from coding_agent.tools.registry import Tool, ToolRegistry

DEFAULT_LINE_LIMIT = 500
DEFAULT_GLOB_LIMIT = 200
DEFAULT_SEARCH_MATCHES = 100


def _is_under_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def create_file_tools(working_dir: Path, line_limit: int = DEFAULT_LINE_LIMIT) -> ToolRegistry:
    registry = ToolRegistry()

    def read_file(path: str) -> str:
        resolved, error = resolve_safe_path(working_dir, path)
        if error:
            return error
        assert resolved is not None
        if not resolved.is_file():
            return f"Error: file not found: {path}"
        lines = resolved.read_text(encoding="utf-8").splitlines()
        if len(lines) > line_limit:
            content = "\n".join(lines[:line_limit])
            text = (
                f"{content}\n\n"
                f"[truncated: file has {len(lines)} lines, showing first {line_limit}]"
            )
        else:
            text = "\n".join(lines)
        return redact_secrets(text)

    def write_file(path: str, content: str) -> str:
        resolved, error = resolve_safe_path(working_dir, path)
        if error:
            return error
        assert resolved is not None
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return f"Successfully wrote {path}"

    def list_dir(path: str = ".") -> str:
        resolved, error = resolve_safe_path(working_dir, path)
        if error:
            return error
        assert resolved is not None
        if not resolved.is_dir():
            return f"Error: directory not found: {path}"
        entries = sorted(resolved.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        if not entries:
            return "(empty directory)"
        return "\n".join(f"{e.name}/" if e.is_dir() else e.name for e in entries)

    def glob_files(pattern: str, path: str = ".") -> str:
        resolved, error = resolve_safe_path(working_dir, path)
        if error:
            return error
        assert resolved is not None
        if not resolved.is_dir():
            return f"Error: directory not found: {path}"
        matches: list[str] = []
        for match in sorted(resolved.glob(pattern)):
            if not _is_under_root(match, working_dir):
                continue
            if match.is_file():
                matches.append(str(match.relative_to(working_dir)).replace("\\", "/"))
            if len(matches) >= DEFAULT_GLOB_LIMIT:
                break
        if not matches:
            return "(no matches)"
        suffix = ""
        if len(matches) >= DEFAULT_GLOB_LIMIT:
            suffix = f"\n[truncated: showing first {DEFAULT_GLOB_LIMIT} matches]"
        return "\n".join(matches) + suffix

    def search_code(
        pattern: str,
        path: str = ".",
        fixed_string: bool = False,
    ) -> str:
        resolved, error = resolve_safe_path(working_dir, path)
        if error:
            return error
        assert resolved is not None
        if not resolved.is_dir():
            return f"Error: directory not found: {path}"
        try:
            regex = re.compile(re.escape(pattern) if fixed_string else pattern)
        except re.error as exc:
            return f"Error: invalid search pattern: {exc}"
        matches: list[str] = []
        root = working_dir.resolve()
        for file_path in sorted(resolved.rglob("*")):
            if not file_path.is_file() or not _is_under_root(file_path, root):
                continue
            try:
                text = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            rel = str(file_path.relative_to(root)).replace("\\", "/")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if regex.search(line):
                    snippet = redact_secrets(line.strip())
                    matches.append(f"{rel}:{line_no}: {snippet}")
                    if len(matches) >= DEFAULT_SEARCH_MATCHES:
                        return (
                            "\n".join(matches)
                            + f"\n[truncated: showing first {DEFAULT_SEARCH_MATCHES} matches]"
                        )
        if not matches:
            return "(no matches)"
        return "\n".join(matches)

    def edit_file(path: str, old_string: str, new_string: str) -> str:
        resolved, error = resolve_safe_path(working_dir, path)
        if error:
            return error
        assert resolved is not None
        if not resolved.is_file():
            return f"Error: file not found: {path}"
        content = resolved.read_text(encoding="utf-8")
        count = content.count(old_string)
        if count == 0:
            return f"Error: old_string not found in {path}"
        if count > 1:
            return f"Error: old_string appears {count} times in {path}; must be unique"
        resolved.write_text(
            content.replace(old_string, new_string, 1),
            encoding="utf-8",
        )
        return f"Successfully edited {path}"

    registry.register(
        Tool(
            name="read_file",
            description="Read the contents of a file relative to the working directory.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path"},
                },
                "required": ["path"],
            },
            func=read_file,
        )
    )
    registry.register(
        Tool(
            name="write_file",
            description="Write content to a file relative to the working directory.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path"},
                    "content": {"type": "string", "description": "File content to write"},
                },
                "required": ["path", "content"],
            },
            func=write_file,
        )
    )
    registry.register(
        Tool(
            name="list_dir",
            description="List files and subdirectories in a directory relative to the working directory.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path (default: .)",
                    },
                },
                "required": [],
            },
            func=list_dir,
        )
    )
    registry.register(
        Tool(
            name="glob_files",
            description="Find files matching a glob pattern under a directory.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g. **/*.py)",
                    },
                    "path": {
                        "type": "string",
                        "description": "Relative directory to search (default: .)",
                    },
                },
                "required": ["pattern"],
            },
            func=glob_files,
        )
    )
    registry.register(
        Tool(
            name="search_code",
            description="Search file contents under a directory for a regex or fixed string.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex or fixed string"},
                    "path": {
                        "type": "string",
                        "description": "Relative directory to search (default: .)",
                    },
                    "fixed_string": {
                        "type": "boolean",
                        "description": "Treat pattern as literal text (default: false)",
                    },
                },
                "required": ["pattern"],
            },
            func=search_code,
        )
    )
    registry.register(
        Tool(
            name="edit_file",
            description="Replace a unique old_string with new_string in a file.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path"},
                    "old_string": {"type": "string", "description": "Text to replace"},
                    "new_string": {"type": "string", "description": "Replacement text"},
                },
                "required": ["path", "old_string", "new_string"],
            },
            func=edit_file,
        )
    )
    return registry
