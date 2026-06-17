## ADDED Requirements

### Requirement: CLI log level flag

The CLI SHALL accept an optional `--log-level` flag with values `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` that configures operational logging for the process.

#### Scenario: Debug flag enables verbose logs

- **WHEN** the user runs `coding-agent --log-level DEBUG`
- **THEN** operational loggers emit DEBUG and above for the session

### Requirement: CLI operational errors use logging

Non-user-facing CLI failures (configuration errors, unexpected LLM failures before user formatting) SHALL be recorded via the operational logger at ERROR level while still presenting a concise message to the user on stderr.

#### Scenario: Config error logged and displayed

- **WHEN** startup fails due to `ConfigError`
- **THEN** the error is logged at ERROR and a user-readable message is written to stderr
