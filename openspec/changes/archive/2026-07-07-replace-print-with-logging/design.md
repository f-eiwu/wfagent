## Context

Today all runtime output uses `print(..., file=sys.stderr)` or `print(..., file=stream)` across four modules (~40 call sites). TUI mode already routes agent progress through callbacks (`on_step`, `on_tool_call`, etc.); plain mode and the agent fallback path print directly. No logger hierarchy exists; tests cannot assert on log output without patching `print`.

Constraints:
- TUI conversation content must remain callback-driven (not interleaved via stderr logging)
- Slash commands accept an optional `stream` (e.g. `StringIO` in TUI) for captured user output
- Secrets must never appear in logs (existing redaction policies apply to tool output, not log config)

## Goals / Non-Goals

**Goals:**
- Single `setup_logging(level: str)` invoked at process start
- Module loggers via `logging.getLogger(__name__)` in `agent`, `llm`, `cli`, `tools`
- Agent `_log_progress` uses `logger.info` when `on_step` is `None`
- Configurable log level: env `CODING_AGENT_LOG_LEVEL`, optional `.coding-agent.toml` `log_level`, CLI `--log-level` (highest priority)
- User-facing CLI text (help tables, `/status` blocks, session picker) routed through `user_io.write(stream, text)` — plain writes, no log level prefix — to preserve current UX and TUI `StringIO` capture

**Non-Goals:**
- File handlers, log rotation, or external log shipping
- Logging inside TUI widgets or render paths
- Replacing stdout assistant answers in plain mode with logging
- Changing LLM SDK internal logging

## Decisions

### 1. Split operational logging vs user I/O

**Decision:** Use stdlib `logging` for operational/diagnostic events; use `user_io.write(stream, text)` for deliberate user-facing CLI output.

**Rationale:** Slash `/help` and session tables are product output, not diagnostics. Feeding them through `logging.info` would add timestamps/levels and complicate TUI capture tests.

**Alternative considered:** Log everything including user output → rejected (pollutes logs, breaks `StringIO` slash tests semantics).

### 2. Logger hierarchy and format

**Decision:** Root package logger `coding_agent` with one `StreamHandler` to stderr. Format: `%(levelname)s %(name)s: %(message)s` for operational logs. `user_io` writes raw text (no prefix).

**Rationale:** Simple, grep-friendly, matches common CLI tool patterns.

**Alternative considered:** JSON structured logs → out of scope for demo project.

### 3. Agent progress when callbacks are set

**Decision:** When `on_step` / `on_tool_call` callbacks are provided (TUI/plain interactive), do **not** also log at INFO (avoid duplicate). Log only on the no-callback fallback path.

**Rationale:** TUI spec requires conversation-region rendering, not stderr duplication.

### 4. Log level resolution

**Decision:** Reuse existing `Config.from_sources` merge: default `WARNING` in non-verbose mode or `INFO` as default — use **`INFO`** as default to match current visible step progress in plain mode.

**Rationale:** Plain-mode users currently see step lines; `WARNING` default would hide them. `DEBUG` adds LLM retry detail.

**Alternative:** Default `WARNING`, document that plain step progress requires `INFO` → worse UX regression.

### 5. Idempotent setup

**Decision:** `setup_logging()` clears existing handlers on the `coding_agent` logger and reconfigures; safe to call once from `cli.main`.

**Rationale:** Prevents duplicate handlers in tests that invoke CLI multiple times.

## Risks / Trade-offs

- **[Risk] Test brittleness** — tests asserting stderr via `capsys` for errors may need `caplog` for logged errors → Mitigation: keep user_io writes for slash output; only migrate true diagnostics to logging; update tests incrementally
- **[Risk] Duplicate output in plain mode** — if both callback and logger fire → Mitigation: agent only logs when `on_step is None`
- **[Risk] Log level in config file typo** — Mitigation: validate against `DEBUG|INFO|WARNING|ERROR|CRITICAL`, raise `ConfigError` like other keys

## Migration Plan

1. Add `logging_config.py` + `user_io.py` without changing call sites
2. Migrate `agent.py`, then `cli.py` error paths, then `slash_commands`/`session_picker` to `user_io`
3. Add config keys and CLI flag
4. Update tests; run full pytest
5. README config table row for log level

Rollback: revert module; no data migration.

## Open Questions

- None blocking — default log level `INFO` and user_io split are sufficient for v1.
