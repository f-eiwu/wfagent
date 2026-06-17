## ADDED Requirements

### Requirement: Central logging configuration

The system SHALL configure Python's `logging` module once at application startup with a package-scoped logger hierarchy under `coding_agent`.

#### Scenario: Logging initialized on CLI start

- **WHEN** the user runs `coding-agent`
- **THEN** `setup_logging` runs before any agent task and attaches a stderr `StreamHandler` to the `coding_agent` logger tree

#### Scenario: Idempotent setup

- **WHEN** `setup_logging` is called more than once in the same process
- **THEN** duplicate handlers are not attached to the same logger

### Requirement: Configurable log level

The system SHALL resolve log level from layered configuration: default, user/project config file, environment variable `CODING_AGENT_LOG_LEVEL`, and CLI flag `--log-level` (highest priority).

#### Scenario: CLI overrides file

- **WHEN** `.coding-agent.toml` sets `log_level = "WARNING"` and the user runs `coding-agent --log-level DEBUG`
- **THEN** loggers emit `DEBUG` and above

#### Scenario: Invalid log level rejected

- **WHEN** a config file sets `log_level = "verbose"`
- **THEN** configuration loading fails with a clear error before the agent runs

### Requirement: Operational events use logging

Agent step progress, LLM retry warnings, and internal error conditions SHALL be recorded via the `logging` module at appropriate levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`), not via bare `print`.

#### Scenario: Agent step without UI callback

- **WHEN** `Agent.run` is invoked without an `on_step` callback
- **THEN** step progress lines are emitted through `logging` at INFO level

#### Scenario: Agent step with UI callback

- **WHEN** `Agent.run` is invoked with an `on_step` callback (TUI or plain interactive)
- **THEN** step progress is delivered only through the callback and is not duplicated to the operational logger at INFO

### Requirement: User-facing CLI output separation

Intentional user-facing CLI text (slash command responses, session list tables, startup hints) SHALL be written through a dedicated user-output helper that writes plain text to the target stream without log-level prefixes.

#### Scenario: Slash status in TUI

- **WHEN** the user runs `/status` in TUI mode
- **THEN** status text is captured via the slash command stream argument and rendered in the conversation region without logging formatter prefixes

#### Scenario: Session list on stderr

- **WHEN** the user runs `coding-agent ls`
- **THEN** the session table is written to stderr as plain text suitable for terminal display
