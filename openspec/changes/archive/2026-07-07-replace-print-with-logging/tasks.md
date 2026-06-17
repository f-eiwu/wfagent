## 1. Logging infrastructure

- [x] 1.1 Add `src/coding_agent/logging_config.py` with `setup_logging(level: str)` — stderr handler, `coding_agent` logger tree, idempotent handler setup
- [x] 1.2 Add `src/coding_agent/user_io.py` with `write(stream, text)` and `write_line(stream, text)` for plain user-facing output (no log prefixes)
- [x] 1.3 Add `parse_log_level(value: str) -> int` with validation; raise `ConfigError` on invalid names

## 2. Configuration

- [x] 2.1 Add `log_level` to `Config` with default `INFO`; resolve from file, `CODING_AGENT_LOG_LEVEL`, and CLI
- [x] 2.2 Add `--log-level` CLI option to `cli.py`; call `setup_logging` early in main after config resolution
- [x] 2.3 Extend `config_files.py` — allow `log_level` string key, validate against known level names
- [x] 2.4 Document `log_level` / `CODING_AGENT_LOG_LEVEL` / `--log-level` in README config table

## 3. Migrate call sites

- [x] 3.1 Replace `print` in `agent.py` `_log_progress` fallback with `logger.info` when `on_step is None`
- [x] 3.2 Migrate `cli.py` — operational errors to `logger.error`; startup hints and plain-mode notices via `user_io`; keep user-visible formatting
- [x] 3.3 Migrate `slash_commands.py` — replace `print(..., file=stream)` with `user_io.write` / `user_io.write_line`
- [x] 3.4 Migrate `session_picker.py` — session tables and prompts via `user_io`
- [x] 3.5 Add `logger.debug`/`logger.warning` in `llm.py` for retry and transient failure paths (no behavior change)

## 4. Tests

- [x] 4.1 Add `tests/test_logging_config.py` — valid/invalid levels, idempotent setup, level filtering
- [x] 4.2 Extend `test_agent.py` — headless run emits INFO logs via `caplog`; callback path does not duplicate
- [x] 4.3 Extend `test_config_files.py` — `log_level` from file, env/CLI override, invalid value rejected
- [x] 4.4 Update any `capsys` tests broken by migration to use `caplog` or `user_io` stream assertions
- [x] 4.5 Run full `pytest` suite and fix regressions

## 5. OpenSpec sync

- [x] 5.1 Archive change and sync main specs after implementation (`/opsx-archive`)
