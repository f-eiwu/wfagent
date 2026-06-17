## ADDED Requirements

### Requirement: Models slash command

In interactive mode, the CLI SHALL accept `/models` to list supported models and `/models <id>` to switch the active model.

#### Scenario: List models

- **WHEN** the user types `/models` at the interactive prompt
- **THEN** the CLI prints all supported models to stderr with the current model marked

#### Scenario: Switch model

- **WHEN** the user types `/models gpt-4o` at the interactive prompt
- **THEN** the CLI sets the session model to `gpt-4o` and confirms the switch on stderr

#### Scenario: Invalid model switch

- **WHEN** the user types `/models unknown-model` at the interactive prompt
- **THEN** the CLI prints an error on stderr and does not change the active model

#### Scenario: Slash command does not run agent

- **WHEN** the user types a line starting with `/models`
- **THEN** the CLI handles it as a meta-command and does not invoke the agent

### Requirement: Interactive startup hint

The CLI SHALL print a brief hint about `/models` when entering interactive mode.

#### Scenario: Hint on interactive start

- **WHEN** the user starts interactive mode without `--task`
- **THEN** stderr includes a line mentioning `/models` for listing and switching models

## MODIFIED Requirements

### Requirement: Interactive mode

The CLI SHALL enter an interactive prompt loop when invoked without `--task`, allowing the user to type multiple tasks in sequence until they type `exit` or press Ctrl+C. The loop SHALL also accept slash commands beginning with `/`.

#### Scenario: Interactive session

- **WHEN** the user runs `coding-agent` without `--task`
- **THEN** the CLI displays a prompt, accepts task input or slash commands, runs the agent for tasks, prints the result, and prompts again

#### Scenario: Exit interactive mode

- **WHEN** the user types `exit` at the interactive prompt
- **THEN** the CLI exits gracefully
