## Purpose

Command-line interface for the coding agent.

## Requirements

### Requirement: Interactive mode

The CLI SHALL enter an interactive prompt loop when invoked, allowing the user to type multiple tasks in sequence until they type `exit` or press Ctrl+C. On a TTY, the loop SHALL use the interactive TUI by default; with plain mode enabled, it SHALL use a text prompt. The loop SHALL accept slash commands beginning with `/`.

#### Scenario: Interactive session

- **WHEN** the user runs `coding-agent` on a TTY
- **THEN** the CLI presents the interactive TUI, accepts task input or slash commands, runs the agent for tasks, shows results in the conversation view, and accepts further input

#### Scenario: Interactive session plain mode

- **WHEN** the user runs `coding-agent --plain`
- **THEN** the CLI displays a text prompt, accepts task input or slash commands, runs the agent for tasks, prints the result, and prompts again

#### Scenario: Exit interactive mode

- **WHEN** the user types `exit` at the interactive prompt or TUI input
- **THEN** the CLI exits gracefully

### Requirement: Model slash command

In interactive mode, the CLI SHALL accept `/model` to list available models from the provider and `/model <id>` to switch the active model.

#### Scenario: List models

- **WHEN** the user types `/model` at the interactive prompt
- **THEN** the CLI fetches models from the provider API and prints them to stderr with the current model marked

#### Scenario: Switch model

- **WHEN** the user types `/model gpt-4o` at the interactive prompt
- **THEN** the CLI sets the session model to `gpt-4o` and confirms the switch on stderr

#### Scenario: Invalid model switch

- **WHEN** the user types `/model unknown-model` at the interactive prompt
- **THEN** the CLI prints an error on stderr and does not change the active model

#### Scenario: Slash command does not run agent

- **WHEN** the user types a line starting with `/model`
- **THEN** the CLI handles it as a meta-command and does not invoke the agent

### Requirement: Interactive startup hint

The CLI SHALL surface a brief hint about available slash commands (including `/model`, `/help`, and `/status`) when entering interactive mode.

#### Scenario: Hint on interactive start

- **WHEN** the user starts interactive mode
- **THEN** a hint mentioning slash commands (including `/model`, `/help`, and `/status`) is visible in the TUI header or plain-mode stderr

### Requirement: Plain mode flag

The CLI SHALL accept a `--plain` flag that forces the legacy text prompt loop instead of the interactive TUI.

#### Scenario: Force plain interactive mode

- **WHEN** the user runs `coding-agent --plain` on a TTY
- **THEN** the CLI does not launch the full-screen TUI and uses the text prompt loop

### Requirement: Working directory flag

The CLI SHALL accept a `--cwd` flag to set the agent's working directory (default: current directory).

#### Scenario: Custom working directory

- **WHEN** the user runs `coding-agent --cwd /path/to/project` and submits a task in interactive mode
- **THEN** the agent operates on files within `/path/to/project`

### Requirement: Status slash command

In interactive mode, the CLI SHALL accept `/status` to display current session and runtime status without invoking the agent.

#### Scenario: Status in TUI

- **WHEN** the user types `/status` in the TUI
- **THEN** a system message shows session id, model, working directory, max steps, base URL (no API key), auto-approve state, and run phase

#### Scenario: Status in plain mode

- **WHEN** the user types `/status` in plain interactive mode
- **THEN** the same status fields are printed to stderr

#### Scenario: Status does not run agent

- **WHEN** the user types `/status`
- **THEN** the CLI handles it as a meta-command and does not invoke the agent

### Requirement: Configuration flags

The CLI SHALL accept flags for LLM configuration: `--api-key`, `--model`, `--base-url`, `--max-steps`, and `--yes`/`-y` (auto-approve confirm-tier operations). Security defaults to the operation allowlist (auto reads; confirmed writes, edits, and shell) unless `--yes`/`-y` is set.

#### Scenario: Override model via flag

- **WHEN** the user runs `coding-agent --model gpt-4o` and submits a task in interactive mode
- **THEN** the agent uses `gpt-4o` for LLM calls

#### Scenario: Auto-approve via yes flag

- **WHEN** the user runs `coding-agent -y` without a TTY and submits a task that requests confirm-tier tools
- **THEN** confirm-tier tool calls execute without interactive prompts

### Requirement: Step progress output

The CLI SHALL surface a brief summary of each agent step (tool name called or "thinking") during task execution. In TUI mode, summaries appear in the conversation region; in plain mode, they print to stderr.

#### Scenario: Progress during multi-step task

- **WHEN** the agent executes a task requiring 3 tool calls in interactive mode
- **THEN** the CLI shows 3 step summaries in the conversation region (TUI) or stderr (plain) and the final answer in the conversation region (TUI) or stdout (plain)

### Requirement: Entry point

The package SHALL be invocable as `coding-agent` (console script) and as `python -m coding_agent`.

#### Scenario: Console script invocation

- **WHEN** the user runs `coding-agent --help` after installation
- **THEN** the CLI displays usage information

### Requirement: Resume session flag

The CLI SHALL accept a `--resume <id>` flag that loads a saved session and enters interactive mode.

#### Scenario: Resume by id

- **WHEN** the user runs `coding-agent --resume abc123`
- **THEN** the CLI restores session `abc123` and enters interactive mode with prior conversation visible

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
