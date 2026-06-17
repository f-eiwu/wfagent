## ADDED Requirements

### Requirement: Resume session flag

The CLI SHALL accept a `--resume <id>` flag that loads a saved session and enters interactive mode.

#### Scenario: Resume by id

- **WHEN** the user runs `coding-agent --resume abc123` without `--task`
- **THEN** the CLI restores session `abc123` and enters interactive mode with prior conversation visible

#### Scenario: Resume incompatible with one-shot

- **WHEN** the user runs `coding-agent --resume abc123 --task "do something"`
- **THEN** the CLI prints an error and exits without running the task

### Requirement: Continue session flag

The CLI SHALL accept a `--continue` flag that resumes the most recently updated session for the working directory.

#### Scenario: Continue latest session

- **WHEN** the user runs `coding-agent --continue` in a directory with saved sessions
- **THEN** the CLI loads the latest session and enters interactive mode

### Requirement: Session slash commands

In interactive mode, the CLI SHALL accept `/sessions`, `/resume <id>`, and `/new` in addition to existing slash commands.

#### Scenario: Sessions list

- **WHEN** the user types `/sessions` at the interactive prompt
- **THEN** the CLI lists saved sessions without invoking the agent

#### Scenario: Resume in session

- **WHEN** the user types `/resume abc123` at the interactive prompt
- **THEN** the CLI switches to session `abc123` and shows its conversation history

#### Scenario: New session command

- **WHEN** the user types `/new` at the interactive prompt
- **THEN** the CLI starts a fresh session without exiting interactive mode

#### Scenario: Session slash commands do not run agent

- **WHEN** the user types a line starting with `/sessions`, `/resume`, or `/new`
- **THEN** the CLI handles it as a meta-command and does not invoke the agent

### Requirement: Session id in interactive status

The CLI SHALL display the current session's short id in interactive mode status output.

#### Scenario: Plain mode session id

- **WHEN** the user runs interactive plain mode with an active session
- **THEN** stderr includes the short session id alongside model and working directory
