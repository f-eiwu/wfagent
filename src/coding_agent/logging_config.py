from __future__ import annotations

import logging
import sys

from coding_agent.config import ConfigError

VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
PACKAGE_LOGGER = "coding_agent"
_LOG_FORMAT = "%(levelname)s %(name)s: %(message)s"


def parse_log_level(value: str) -> int:
    name = value.strip().upper()
    if name not in VALID_LOG_LEVELS:
        levels = ", ".join(sorted(VALID_LOG_LEVELS))
        raise ConfigError(f"Invalid log level '{value}'. Use one of: {levels}.")
    return getattr(logging, name)


def setup_logging(level: str) -> None:
    numeric_level = parse_log_level(level)
    logger = logging.getLogger(PACKAGE_LOGGER)
    logger.handlers.clear()
    logger.setLevel(numeric_level)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(numeric_level)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    logger.addHandler(handler)
    logger.propagate = False
