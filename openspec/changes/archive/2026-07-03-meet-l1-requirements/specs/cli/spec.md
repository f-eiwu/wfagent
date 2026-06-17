## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Configuration flags

The CLI SHALL accept flags for LLM configuration: `--api-key`, `--model`, `--base-url`, `--max-steps`, and `--yes`/`-y` (auto-approve confirm-tier operations). Security defaults to the operation allowlist (auto reads; confirmed writes, edits, and shell) unless `--yes`/`-y` is set.

#### Scenario: Override model via flag

- **WHEN** the user runs `coding-agent --model gpt-4o --task "explain this codebase"`
- **THEN** the agent uses `gpt-4o` for LLM calls

#### Scenario: Auto-approve via yes flag

- **WHEN** the user runs `coding-agent -y --task "create hello.py"` without a TTY
- **THEN** confirm-tier tool calls execute without interactive prompts

### Requirement: Interactive startup hint

The CLI SHALL surface a brief hint about available slash commands (including `/model`, `/help`, and `/status`) when entering interactive mode.

#### Scenario: Hint on interactive start

- **WHEN** the user starts interactive mode without `--task`
- **THEN** a hint mentioning slash commands (including `/model`, `/help`, and `/status`) is visible in the TUI header or plain-mode stderr
