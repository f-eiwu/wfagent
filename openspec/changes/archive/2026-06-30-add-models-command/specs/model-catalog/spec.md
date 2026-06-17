## ADDED Requirements

### Requirement: Supported model catalog

The system SHALL maintain a curated list of supported LLM model IDs available for interactive selection.

#### Scenario: Catalog contains provider-prefixed IDs

- **WHEN** the model catalog is loaded
- **THEN** each entry includes a model ID string and a human-readable label

#### Scenario: Default model is in catalog

- **WHEN** the catalog is loaded
- **THEN** the default model (`gpt-4o-mini`) is present in the catalog

### Requirement: Model validation

The system SHALL validate model IDs against the supported catalog before switching.

#### Scenario: Valid model ID

- **WHEN** a user requests switch to a model ID that exists in the catalog
- **THEN** the switch succeeds

#### Scenario: Invalid model ID

- **WHEN** a user requests switch to a model ID not in the catalog
- **THEN** the system rejects the switch with an error message listing valid options

### Requirement: Session-scoped model selection

The system SHALL track the active model for the current interactive session separately from environment variables.

#### Scenario: Session override does not modify environment

- **WHEN** the user switches models via `/models <name>` during a session
- **THEN** subsequent agent runs use the new model and `OPENAI_MODEL` in the process environment is unchanged

#### Scenario: CLI flag seeds session model

- **WHEN** the user starts interactive mode with `--model custom/model`
- **THEN** the session starts with that model even if it is not in the catalog (no validation on startup)
