import fnmatch
from pathlib import Path

SENSITIVE_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*credentials*",
    "*secret*",
    ".git/config",
    "id_rsa",
    "id_rsa.*",
    "*.p12",
    "*.pfx",
)


def _normalize_relative_path(relative_path: str) -> str:
    normalized = relative_path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def is_sensitive_path(relative_path: str) -> bool:
    normalized = _normalize_relative_path(relative_path)
    name = Path(normalized).name
    lower_name = name.lower()

    if lower_name == ".env" or lower_name.startswith(".env."):
        return True

    for pattern in SENSITIVE_PATTERNS:
        if pattern in (".env", ".env.*"):
            continue
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(normalized, pattern):
            return True
    return False


def resolve_safe_path(working_dir: Path, relative_path: str) -> tuple[Path | None, str | None]:
    if is_sensitive_path(relative_path):
        return None, f"Error: path '{relative_path}' is blocked by security policy"

    base = working_dir.resolve()
    candidate = working_dir / _normalize_relative_path(relative_path)

    for part in candidate.parents:
        if part == base:
            break
        if part.is_symlink():
            return None, f"Error: path '{relative_path}' is outside the working directory"

    if candidate.is_symlink():
        return None, f"Error: path '{relative_path}' is outside the working directory"

    try:
        resolved = candidate.resolve()
        resolved.relative_to(base)
    except ValueError:
        return None, f"Error: path '{relative_path}' is outside the working directory"

    return resolved, None
