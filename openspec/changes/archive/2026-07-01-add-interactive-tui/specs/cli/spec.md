## MODIFIED Requirements

### Requirement: Interactive mode

The CLI SHALL enter an interactive prompt loop when invoked without `--task`, allowing the user to type multiple tasks in sequence until they type `exit` or press Ctrl+C. On a TTY, the loop SHALL use the interactive TUI by default; with plain mode enabled, it SHALL use a text prompt. The loop SHALL accept slash commands beginning with `/`.

#### Scenario: Interactive session

- **WHEN** the user runs `coding-agent` without `--task` on a TTY
- **THEN** the CLI presents the interactive TUI, accepts task input or slash commands, runs the agent for tasks, shows results in the conversation view, and accepts further input

#### Scenario: Interactive session plain mode

- **WHEN** the user runs `coding-agent --plain` without `--task`
- **THEN** the CLI displays a text prompt, accepts task input or slash commands, runs the agent for tasks, prints the result, and prompts again

#### Scenario: Exit interactive mode

- **WHEN** the user types `exit` at the interactive prompt or TUI input
- **THEN** the CLI exits gracefully

### Requirement: Interactive startup hint

The CLI SHALL surface a brief hint about available slash commands (including `/model` and `/help`) when entering interactive mode.

#### Scenario: Hint on interactive start

- **WHEN** the user starts interactive mode without `--task`
- **THEN** a hint mentioning slash commands (including `/model` and `/help`) is visible in the TUI header or plain-mode stderr

## ADDED Requirements

### Requirement: Plain mode flag

The CLI SHALL accept a `--plain` flag that forces the legacy text prompt loop instead of the interactive TUI.

#### Scenario: Force plain interactive mode

- **WHEN** the user runs `coding-agent --plain` without `--task` on a TTY
- **THEN** the CLI does not launch the full-screen TUI and uses the text prompt loop

### Requirement: Step progress output

The CLI SHALL surface a brief summary of each agent step (tool name called or "thinking") during task execution. In TUI mode, summaries appear in the conversation region; in plain and one-shot modes, they print to stderr.

#### Scenario: Progress during multi-step task

- **WHEN** the agent executes a task requiring 3 tool calls
- **THEN** the CLI shows 3 step summaries in the conversation region (TUI) or stderr (plain/one-shot) and the final answer on stdout (one-shot) or in the conversation region (TUI)
