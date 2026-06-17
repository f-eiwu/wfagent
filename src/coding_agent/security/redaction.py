import re
from pathlib import Path

REDACTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"sk-[a-zA-Z0-9]{10,}"), "sk-[REDACTED]"),
    (re.compile(r"Bearer\s+\S+", re.I), "Bearer [REDACTED]"),
    (re.compile(r"(?i)(password|passwd|api[_-]?key|secret|token)\s*[=:]\s*\S+"), r"\1=[REDACTED]"),
    (re.compile(r"\b[a-f0-9]{32,}\b"), "[REDACTED]"),
]

_CLI_API_KEY = re.compile(
    r"(--api-key\s+)(?:\"([^\"]*)\"|'([^']*)'|(\S+))",
    re.IGNORECASE,
)
_ENV_API_KEY = re.compile(
    r"((?:\$env:)?OPENAI_API_KEY\s*=\s*)(?:\"([^\"]*)\"|'([^']*)'|(\S+))",
    re.IGNORECASE,
)
_PY_API_KEY_KWARG = re.compile(
    r"(api_key\s*=\s*)(?:'([^']*)'|\"([^\"]*)\")",
    re.IGNORECASE,
)
_SAFE_EXPORT_VALUES = frozenset({"[REDACTED]", "<url>", "<redacted>"})
_RAW_API_KEY_IN_EXPORT = re.compile(
    r'--api-key\s+"(?!\[REDACTED\])[^"]*"',
    re.IGNORECASE,
)
_EXAMPLE_KEY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b[a-f0-9]{8,}(?:\.{3})\b", re.I), "[REDACTED]"),
    (re.compile(r"\bsk-your-key\b", re.I), "sk-[REDACTED]"),
    (re.compile(r"\byour-azure-key\b", re.I), "[REDACTED]"),
    (re.compile(r"\bsk-\.\.\."), "sk-[REDACTED]"),
    (re.compile(r"set OPENAI_API_KEY=sk-\.\.\.", re.I), "set OPENAI_API_KEY=[REDACTED]"),
    (re.compile(r"export OPENAI_API_KEY=sk-your-key", re.I), "export OPENAI_API_KEY=[REDACTED]"),
]
_UNREDACTED_EXAMPLE_KEYS = re.compile(
    r"sk-your-key|your-azure-key|sk-\.\.\.|--api-key\s+\"\.\.\.\"",
    re.IGNORECASE,
)


def redact_secrets(text: str) -> str:
    result = text
    for pattern, replacement in REDACTION_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def _redact_quoted_value(prefix: str, value: str, *, quote: str) -> str:
    if value in _SAFE_EXPORT_VALUES or value.startswith("["):
        return f"{prefix}{quote}{value}{quote}"
    return f'{prefix}"[REDACTED]"' if quote == '"' else f"{prefix}'[REDACTED]'"


def redact_session_export(text: str) -> str:
    """Redact API keys in session export markdown without corrupting code citations."""

    def replace_cli(match: re.Match[str]) -> str:
        prefix, dquote, squote, bare = match.groups()
        if dquote is not None:
            return _redact_quoted_value(prefix, dquote, quote='"')
        if squote is not None:
            return _redact_quoted_value(prefix, squote, quote="'")
        if bare in _SAFE_EXPORT_VALUES or bare.startswith("["):
            return match.group(0)
        return f"{prefix}[REDACTED]"

    def replace_env(match: re.Match[str]) -> str:
        prefix, dquote, squote, bare = match.groups()
        if dquote is not None:
            return _redact_quoted_value(prefix, dquote, quote='"')
        if squote is not None:
            return _redact_quoted_value(prefix, squote, quote="'")
        if bare in _SAFE_EXPORT_VALUES or bare.startswith("["):
            return match.group(0)
        return f"{prefix}[REDACTED]"

    def replace_py_kwarg(match: re.Match[str]) -> str:
        prefix, squote, dquote = match.groups()
        value = squote if squote is not None else dquote
        if value in _SAFE_EXPORT_VALUES:
            return match.group(0)
        quote = "'" if squote is not None else '"'
        return _redact_quoted_value(prefix, value, quote=quote)

    result = _CLI_API_KEY.sub(replace_cli, text)
    result = _ENV_API_KEY.sub(replace_env, result)
    result = _PY_API_KEY_KWARG.sub(replace_py_kwarg, result)
    result = re.sub(r"sk-[a-zA-Z0-9]{10,}", "sk-[REDACTED]", result)
    for pattern, replacement in _EXAMPLE_KEY_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def session_export_has_unredacted_secrets(text: str) -> bool:
    return (
        _RAW_API_KEY_IN_EXPORT.search(text) is not None
        or _UNREDACTED_EXAMPLE_KEYS.search(text) is not None
    )


def anonymize_logs_dir(logs_dir: Path) -> list[Path]:
    """Redact secrets in all files under logs_dir. Returns paths that were updated."""
    updated: list[Path] = []
    if not logs_dir.is_dir():
        return updated
    for path in sorted(logs_dir.iterdir()):
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8")
        redacted = redact_session_export(original)
        if redacted != original:
            path.write_text(redacted, encoding="utf-8")
            updated.append(path)
    return updated
