## ADDED Requirements

### Requirement: Destructive tool confirmation

The agent SHALL prompt the user for confirmation on stderr before executing a destructive tool call, unless auto-approve is enabled.

#### Scenario: Confirm shell command

- **WHEN** auto-approve is false and the LLM requests a `run_shell` tool call
- **THEN** the agent prints a confirmation prompt and waits for user input before executing

#### Scenario: Confirm file overwrite

- **WHEN** auto-approve is false and the LLM requests `write_file` on a path that already exists
- **THEN** the agent prints a confirmation prompt and waits for user input before executing

#### Scenario: Auto-approve skips prompt

- **WHEN** auto-approve is true and the LLM requests a destructive tool call
- **THEN** the agent executes the tool without prompting

#### Scenario: User rejects action

- **WHEN** the user responds with anything other than `y` or `yes` at the confirmation prompt
- **THEN** the agent skips the tool call and returns a rejection message to the LLM

#### Scenario: Non-interactive without auto-approve

- **WHEN** stdin is not a TTY, auto-approve is false, and a destructive tool call is requested
- **THEN** the agent rejects the tool call with an error indicating confirmation is required

### Requirement: Non-destructive tools execute without prompt

The agent SHALL execute `read_file` and `list_dir` tool calls without confirmation prompts.

#### Scenario: Read file without prompt

- **WHEN** the LLM requests a `read_file` tool call
- **THEN** the agent executes it immediately without user confirmation
