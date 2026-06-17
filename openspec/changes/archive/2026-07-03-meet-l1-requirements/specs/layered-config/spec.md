## ADDED Requirements

### Requirement: User-level configuration file

The system SHALL load optional user-level settings from a TOML file at `~/.config/coding-agent/config.toml` on Unix or `%APPDATA%/coding-agent/config.toml` on Windows.

#### Scenario: User file provides default model

- **WHEN** the user config file sets `model = "gpt-4o-mini"` and no project file or CLI flag overrides it
- **THEN** the agent uses `gpt-4o-mini` as the default model

### Requirement: Project-level configuration file

The system SHALL load optional project-level settings from `.coding-agent.toml` in the working directory.

#### Scenario: Project file overrides user file

- **WHEN** the user file sets `max_steps = 20` and the project file sets `max_steps = 30`
- **THEN** the resolved `max_steps` is 30

### Requirement: Configuration merge priority

Settings SHALL resolve in ascending priority: hardcoded defaults, user config file, project config file, environment variables, CLI flags.

#### Scenario: CLI flag wins over project file

- **WHEN** the project file sets `model = "a"` and the user runs `coding-agent --model b`
- **THEN** the agent uses model `b`

#### Scenario: Environment variable wins over project file

- **WHEN** the project file sets `base_url = "https://example.com/v1"` and `OPENAI_BASE_URL` is set to `https://other.com/v1`
- **THEN** the agent uses `https://other.com/v1`

### Requirement: Configurable fields in files

Config files MAY set `model`, `base_url`, `max_steps`, and `request_timeout` (LLM HTTP timeout in seconds).

#### Scenario: Request timeout from project file

- **WHEN** `.coding-agent.toml` sets `request_timeout = 90`
- **THEN** LLM API calls use a 90-second timeout unless overridden by CLI or env

### Requirement: API keys excluded from config files

The system SHALL NOT read API keys from config files. API keys SHALL only come from `OPENAI_API_KEY` or `--api-key`.

#### Scenario: api_key in config file rejected

- **WHEN** a config file contains an `api_key` field
- **THEN** the CLI exits with a clear error before making any LLM call

#### Scenario: Config display never shows secrets

- **WHEN** the user runs `/status` or views configuration help
- **THEN** no API key value is printed
