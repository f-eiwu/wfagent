## MODIFIED Requirements

### Requirement: Configurable fields in files

Config files MAY set `model`, `base_url`, `max_steps`, `request_timeout` (LLM HTTP timeout in seconds), `max_context_tokens`, `tool_result_max_chars`, `context_keep_recent_messages`, and `log_level`.

#### Scenario: Request timeout from project file

- **WHEN** `.coding-agent.toml` sets `request_timeout = 90`
- **THEN** LLM API calls use a 90-second timeout unless overridden by CLI or env

#### Scenario: Context budget from project file

- **WHEN** `.coding-agent.toml` sets `max_context_tokens = 6000`
- **THEN** the agent compresses LLM-bound history to fit approximately 6000 estimated tokens

#### Scenario: Tool result limit from user file

- **WHEN** the user config sets `tool_result_max_chars = 2000`
- **THEN** tool message bodies in LLM requests are truncated at 2000 characters

#### Scenario: Log level from project file

- **WHEN** `.coding-agent.toml` sets `log_level = "DEBUG"`
- **THEN** operational loggers emit DEBUG and above unless overridden by env or CLI

## ADDED Requirements

### Requirement: Log level environment override

The system SHALL read `CODING_AGENT_LOG_LEVEL` from the environment with higher priority than config file defaults and lower priority than the CLI `--log-level` flag.

#### Scenario: Environment overrides file

- **WHEN** the user config sets `log_level = "WARNING"` and `CODING_AGENT_LOG_LEVEL=INFO`
- **THEN** operational loggers emit INFO and above
