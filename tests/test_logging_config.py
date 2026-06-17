import logging

import pytest

from coding_agent.config import ConfigError
from coding_agent.logging_config import PACKAGE_LOGGER, parse_log_level, setup_logging


class TestParseLogLevel:
    def test_accepts_standard_levels(self):
        assert parse_log_level("debug") == logging.DEBUG
        assert parse_log_level("INFO") == logging.INFO
        assert parse_log_level("warning") == logging.WARNING

    def test_rejects_invalid_level(self):
        with pytest.raises(ConfigError, match="Invalid log level"):
            parse_log_level("verbose")


class TestSetupLogging:
    def test_idempotent_handler_setup(self):
        setup_logging("INFO")
        logger = logging.getLogger(PACKAGE_LOGGER)
        first_count = len(logger.handlers)
        setup_logging("DEBUG")
        assert len(logger.handlers) == first_count

    def test_level_filtering(self, capsys):
        setup_logging("WARNING")
        logger = logging.getLogger("coding_agent.agent")
        logger.info("should not appear")
        logger.warning("should appear")
        captured = capsys.readouterr()
        assert "should not appear" not in captured.err
        assert "should appear" in captured.err

    def test_debug_level_emits_info(self, capsys):
        setup_logging("DEBUG")
        logger = logging.getLogger("coding_agent.agent")
        logger.info("visible info")
        captured = capsys.readouterr()
        assert "visible info" in captured.err
