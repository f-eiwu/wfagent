import re

BLOCKED_PATTERNS = [
    re.compile(r"rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+|--force\s+).*(/\s*)?$", re.I),
    re.compile(r"rm\s+-rf\b", re.I),
    re.compile(r"rm\s+-r\s+/", re.I),
    re.compile(r"\bdel\s+/[fqFQ]", re.I),
    re.compile(r"\bformat\s+[a-zA-Z]:", re.I),
    re.compile(r"mkfs\.", re.I),
    re.compile(r"dd\s+if=", re.I),
    re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;", re.I),
    re.compile(r"curl\s+[^\s|]*\s*\|\s*(ba)?sh", re.I),
    re.compile(r"wget\s+[^\s|]*\s*\|\s*(ba)?sh", re.I),
    re.compile(r"curl\s+[^\s|]*\s*\|\s*sudo\s+(ba)?sh", re.I),
    re.compile(r">\s*/dev/sd[a-z]", re.I),
    re.compile(r"shutdown\b", re.I),
    re.compile(r"reboot\b", re.I),
    re.compile(r"poweroff\b", re.I),
]

SHELL_METACHARACTERS = set("|&;<>$`")


def is_command_allowed(command: str) -> bool:
    normalized = command.strip()
    if not normalized:
        return False
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(normalized):
            return False
    return True


def needs_shell(command: str) -> bool:
    return any(char in command for char in SHELL_METACHARACTERS)
