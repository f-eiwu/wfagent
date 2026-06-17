## Why

The codebase uses scattered `print()` calls for agent progress, errors, and CLI output (`agent.py`, `cli.py`, `slash_commands.py`, `session_picker.py`). There is no `logging` module usage, which limits log levels, testability, and operational traceability. The evaluate-agent rubric flagged this as a gap in engineering completeness.

## What Changes

- Add a **central logging setup** module with configurable level (default `INFO`, overridable via env/CLI)
- Replace **diagnostic `print` calls** in agent core and LLM/tool paths with structured `logging` (`DEBUG`/`INFO`/`WARNING`/`ERROR`)
- Introduce a thin **`user_io` helper** for intentional user-facing CLI text (slash output, session tables, startup hints) so operational logs and user messages are not conflated
- Wire logging initialization once at CLI entry (`coding-agent` main)
- Add tests for log level configuration and that agent step progress uses the logger when no UI callback is registered
- Document `CODING_AGENT_LOG_LEVEL` (and optional `--log-level`) in README

## Capabilities

### New Capabilities

- `application-logging`: Central logger configuration, module loggers, and separation of operational logs from user-facing CLI output

### Modified Capabilities

- `agent-core`: Agent step progress and internal events SHALL use the logging module instead of `print` when no UI callback is provided
- `cli`: CLI startup, errors, and plain-mode progress SHALL route operational messages through logging; user-facing slash/session output uses the user I/O helper
- `layered-config`: Add optional `log_level` config key and env var with merge priority consistent with other settings

## Impact

- **Code:** new `logging_config.py` (or `log_config.py`), optional `user_io.py`; edits to `agent.py`, `cli.py`, `slash_commands.py`, `session_picker.py`, `config.py`, `config_files.py`
- **APIs:** `Config` gains `log_level`; `setup_logging()` called from CLI `main`
- **Dependencies:** none (stdlib `logging` only)
- **Tests:** new `tests/test_logging_config.py`; extend `test_agent.py`, `test_cli.py`, `test_config_files.py`
- **Out of scope:** log file rotation, structured JSON logs, third-party observability sinks, changing TUI conversation rendering (still callback-driven)
