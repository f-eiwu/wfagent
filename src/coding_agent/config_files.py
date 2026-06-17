from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path
from typing import Any

from coding_agent.config import ConfigError
from coding_agent.logging_config import parse_log_level

FORBIDDEN_KEYS = frozenset({"api_key"})
ALLOWED_KEYS = frozenset(
    {
        "model",
        "base_url",
        "max_steps",
        "request_timeout",
        "log_level",
    }
)
INTEGER_KEYS = frozenset(
    {
        "max_steps",
        "request_timeout",
    }
)
STRING_KEYS = frozenset({"model", "base_url", "log_level"})


def _validate_config_types(data: dict[str, Any], source: str) -> None:
    for key, value in data.items():
        if key in FORBIDDEN_KEYS:
            continue
        if key not in ALLOWED_KEYS:
            raise ConfigError(f"Unknown config key '{key}' in {source}.")
        if key in INTEGER_KEYS:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ConfigError(
                    f"Config field '{key}' in {source} must be an integer."
                )
        elif key in STRING_KEYS and not isinstance(value, str):
            raise ConfigError(f"Config field '{key}' in {source} must be a string.")
        if key == "log_level":
            parse_log_level(str(value))


def user_config_path() -> Path:
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        return Path(appdata) / "coding-agent" / "config.toml"
    return Path.home() / ".config" / "coding-agent" / "config.toml"


def project_config_path(working_dir: Path) -> Path:
    return working_dir / ".coding-agent.toml"


def _reject_forbidden_keys(data: dict[str, Any], source: str) -> None:
    for key in FORBIDDEN_KEYS:
        if key in data:
            raise ConfigError(
                f"Config file {source} must not contain '{key}'. "
                "Set OPENAI_API_KEY or use --api-key instead."
            )


def load_config_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        return {}
    _reject_forbidden_keys(data, str(path))
    _validate_config_types(data, str(path))
    return data


def load_layered_file_config(working_dir: Path) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    user_path = user_config_path()
    project_path = project_config_path(working_dir)
    merged.update(load_config_file(user_path))
    merged.update(load_config_file(project_path))
    return merged
