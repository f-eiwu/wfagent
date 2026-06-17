## Purpose

Provider model discovery, validation, and session-scoped model selection.

## Requirements

### Requirement: Provider model list

The system SHALL fetch available LLM model IDs from the configured provider API (`GET /v1/models`) when the user runs `/model` in interactive mode.

#### Scenario: Fetch models from provider

- **WHEN** the user types `/model` at the interactive prompt
- **THEN** the system calls the provider models API using the configured API key and base URL

#### Scenario: Provider fetch failure

- **WHEN** the provider models API returns an error or empty list
- **THEN** the system prints an error to stderr and does not change the active model

### Requirement: Model validation

The system SHALL validate model IDs against the fetched provider list before switching.

#### Scenario: Valid model ID

- **WHEN** a user requests switch to a model ID returned by the provider
- **THEN** the switch succeeds

#### Scenario: Invalid model ID

- **WHEN** a user requests switch to a model ID not in the fetched list
- **THEN** the system rejects the switch with an error message

### Requirement: Session-scoped model selection

The system SHALL track the active model for the current interactive session separately from environment variables.

#### Scenario: Session override does not modify environment

- **WHEN** the user switches models via `/model <name>` during a session
- **THEN** subsequent agent runs use the new model and `OPENAI_MODEL` in the process environment is unchanged

#### Scenario: CLI flag seeds session model

- **WHEN** the user starts interactive mode with `--model custom/model`
- **THEN** the session starts with that model without requiring provider-list validation on startup
