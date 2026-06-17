## ADDED Requirements

### Requirement: Allow shell flag

The CLI SHALL accept an `--allow-shell` flag that enables the `run_shell` tool.

#### Scenario: Enable shell tool

- **WHEN** the user runs `coding-agent --allow-shell --task "run tests"`
- **THEN** the agent registers the `run_shell` tool for the session

#### Scenario: Shell disabled without flag

- **WHEN** the user runs `coding-agent --task "run tests"` without `--allow-shell`
- **THEN** the `run_shell` tool is not available to the LLM

### Requirement: Auto-approve flag

The CLI SHALL accept a `--yes` flag that skips confirmation prompts for destructive tool calls.

#### Scenario: Skip confirmation prompts

- **WHEN** the user runs `coding-agent --yes --allow-shell --task "delete temp files"`
- **THEN** destructive tool calls execute without user confirmation prompts

### Requirement: Security warning on startup

The CLI SHALL print a brief security notice to stderr when `--allow-shell` or `--yes` is used.

#### Scenario: Warning when shell enabled

- **WHEN** the user runs `coding-agent --allow-shell --task "test"`
- **THEN** stderr includes a warning that shell commands will be executed

#### Scenario: Warning when auto-approve enabled

- **WHEN** the user runs `coding-agent --yes --task "test"`
- **THEN** stderr includes a warning that destructive actions will not be confirmed

## MODIFIED Requirements

### Requirement: Configuration flags

The CLI SHALL accept flags for LLM configuration: `--api-key`, `--model`, `--base-url`, and `--max-steps`, plus security flags `--allow-shell` and `--yes`.

#### Scenario: Override model via flag

- **WHEN** the user runs `coding-agent --model gpt-4o --task "explain this codebase"`
- **THEN** the agent uses `gpt-4o` for LLM calls
