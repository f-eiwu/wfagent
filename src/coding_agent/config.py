import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

class ConfigError(Exception):
    """Raised when configuration is invalid."""


DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MAX_STEPS = 20
DEFAULT_REQUEST_TIMEOUT = 120
DEFAULT_LOG_LEVEL = "INFO"


def _coerce_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ConfigError(f"Config field '{field}' must be an integer.")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Config field '{field}' must be an integer.") from exc


def _resolve_string(
    cli_value: str | None,
    env_value: str | None,
    file_config: dict[str, Any],
    file_key: str,
    default: str,
) -> str:
    if cli_value is not None:
        return cli_value
    if env_value:
        return env_value
    file_value = file_config.get(file_key)
    if file_value is not None:
        return str(file_value)
    return default


def _resolve_int(
    cli_value: int | None,
    env_value: str | None,
    file_config: dict[str, Any],
    file_key: str,
    default: int,
) -> int:
    if cli_value is not None:
        return cli_value
    if env_value:
        return _coerce_int(env_value, file_key)
    if file_key in file_config:
        return _coerce_int(file_config[file_key], file_key)
    return default


@dataclass
class Config:
    api_key: str
    model: str
    base_url: str
    max_steps: int
    working_dir: Path
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT
    log_level: str = DEFAULT_LOG_LEVEL
    auto_approve: bool = False

    @classmethod
    def from_sources(
        cls,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        max_steps: int | None = None,
        request_timeout: int | None = None,
        log_level: str | None = None,
        cwd: str | None = None,
        auto_approve: bool = False,
    ) -> "Config":
        resolved_cwd = Path(cwd) if cwd else Path.cwd()
        working_dir = resolved_cwd.resolve()
        from coding_agent.config_files import load_layered_file_config

        file_config = load_layered_file_config(working_dir)

        resolved_api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        resolved_model = _resolve_string(
            model,
            os.environ.get("OPENAI_MODEL"),
            file_config,
            "model",
            DEFAULT_MODEL,
        )
        resolved_base_url = _resolve_string(
            base_url,
            os.environ.get("OPENAI_BASE_URL"),
            file_config,
            "base_url",
            DEFAULT_BASE_URL,
        )
        resolved_max_steps = _resolve_int(
            max_steps,
            os.environ.get("CODING_AGENT_MAX_STEPS"),
            file_config,
            "max_steps",
            DEFAULT_MAX_STEPS,
        )
        resolved_request_timeout = _resolve_int(
            request_timeout,
            os.environ.get("CODING_AGENT_REQUEST_TIMEOUT"),
            file_config,
            "request_timeout",
            DEFAULT_REQUEST_TIMEOUT,
        )
        resolved_log_level = _resolve_string(
            log_level,
            os.environ.get("CODING_AGENT_LOG_LEVEL"),
            file_config,
            "log_level",
            DEFAULT_LOG_LEVEL,
        )

        config = cls(
            api_key=resolved_api_key,
            model=resolved_model,
            base_url=resolved_base_url,
            max_steps=resolved_max_steps,
            working_dir=working_dir,
            request_timeout=resolved_request_timeout,
            log_level=resolved_log_level,
            auto_approve=auto_approve,
        )
        config.validate()
        return config

    def validate(self) -> None:
        from coding_agent.logging_config import parse_log_level

        parse_log_level(self.log_level)
        if not self.api_key:
            raise ConfigError(
                "API key is required. Set OPENAI_API_KEY environment variable "
                "or pass --api-key."
            )
        if not self.working_dir.is_dir():
            self.working_dir.mkdir(parents=True, exist_ok=True)
