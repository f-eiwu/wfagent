## Purpose

User confirmation before destructive agent actions.

## Requirements

### Requirement: Destructive tool confirmation

The agent SHALL prompt the user for confirmation before executing confirm-tier tool calls (`write_file`, `run_shell`) unless the operation is on the session allowlist.

#### Scenario: Confirm shell command

- **WHEN** the LLM requests a `run_shell` tool call that is not on the session allowlist
- **THEN** the agent prints a confirmation prompt and waits for user input before executing

#### Scenario: Confirm file write

- **WHEN** the LLM requests `write_file` that is not on the session allowlist
- **THEN** the agent prints a confirmation prompt and waits for user input before executing

#### Scenario: Allowlisted operation skips prompt

- **WHEN** the LLM requests a confirm-tier tool call that is already on the session allowlist
- **THEN** the agent executes the tool without prompting

#### Scenario: User rejects action

- **WHEN** the user responds with anything other than `y` or `yes` at the confirmation prompt
- **THEN** the agent skips the tool call and returns a rejection message to the LLM

#### Scenario: Non-interactive without allowlist entry

- **WHEN** stdin is not a TTY, the operation is not on the allowlist, and a confirm-tier tool call is requested
- **THEN** the agent rejects the tool call with an error indicating confirmation is required

### Requirement: Non-destructive tools execute without prompt

The agent SHALL execute `read_file` and `list_dir` tool calls without confirmation prompts.

#### Scenario: Read file without prompt

- **WHEN** the LLM requests a `read_file` tool call
- **THEN** the agent executes it immediately without user confirmation
