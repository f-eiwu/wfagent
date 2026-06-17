## Purpose

Full-screen interactive terminal UI for multi-turn coding agent sessions.

## Requirements

### Requirement: Full-screen interactive layout

When interactive mode runs on a TTY without plain mode, the CLI SHALL present a full-screen terminal UI with a header region, scrollable conversation region, bottom input region, and status footer.

#### Scenario: TUI launches on interactive start

- **WHEN** the user runs `coding-agent` on a TTY without plain mode enabled
- **THEN** the CLI occupies the terminal with a structured layout instead of a bare `task>` line prompt

#### Scenario: Plain mode bypasses TUI

- **WHEN** the user runs `coding-agent` with `CODING_AGENT_PLAIN_PROMPT=1` or `--plain`
- **THEN** the CLI uses the existing text prompt loop and does not launch the full-screen TUI

### Requirement: Conversation history display

The TUI SHALL retain and display all user messages, assistant replies, and system notices for the current session in chronological order within the conversation region.

#### Scenario: User message styling

- **WHEN** the user submits a task or command that is shown as a user turn
- **THEN** the message appears in a visually distinct block (e.g. highlighted bar) in the conversation region

#### Scenario: Assistant reply styling

- **WHEN** the agent completes a task and returns a final response
- **THEN** the response appears as assistant text below the corresponding user message in the conversation region

#### Scenario: Scrollback

- **WHEN** the conversation exceeds the visible height
- **THEN** the user can scroll the conversation region to view earlier turns

### Requirement: Bottom input area

The TUI SHALL provide a fixed bottom input field for follow-up messages with a visible prompt indicator and placeholder text indicating follow-up input is expected.

#### Scenario: Submit follow-up

- **WHEN** the user types text in the input area and submits (Enter)
- **THEN** the input is processed as the next interactive line (task, `exit`, or slash command) and the input field clears

#### Scenario: Placeholder hint

- **WHEN** the input field is empty and focused
- **THEN** placeholder text such as "Add a follow-up" is visible

### Requirement: Slash commands in TUI input

The TUI input SHALL support the same slash commands as plain interactive mode (`/model`, `/help`, etc.) with visual highlighting for recognized commands while typing.

#### Scenario: Slash command handled in TUI

- **WHEN** the user submits `/model` in the TUI input
- **THEN** the command is handled without invoking the agent and the result appears in the conversation region

### Requirement: Tool call visibility in conversation

During agent execution in TUI mode, the conversation region SHALL display each tool call with the tool name and a summary of arguments before execution.

#### Scenario: Write tool call shown

- **WHEN** the LLM requests `write_file` for path `hello.py`
- **THEN** a system notice such as `Tool call: write_file path=hello.py` appears in the conversation region

### Requirement: Tool result visibility in conversation

During agent execution in TUI mode, the conversation region SHALL display a summary of each tool result after execution.

#### Scenario: Tool result shown after read

- **WHEN** `read_file` completes successfully
- **THEN** a system notice such as `Tool result: read_file — <summary>` appears in the conversation region

### Requirement: Rejection visibility in conversation

When the user rejects a confirm-tier operation, the conversation region SHALL display the rejection before the agent continues.

#### Scenario: User rejects shell command

- **WHEN** the user responds `n` to a shell approval prompt
- **THEN** a system notice such as `Rejected: run_shell command=...` appears in the conversation region

### Requirement: Streaming assistant output in TUI

While the LLM generates a final text response, the TUI SHALL incrementally display assistant content in the conversation region when streaming is active.

#### Scenario: Tokens appear during generation

- **WHEN** the LLM streams content chunks during a task
- **THEN** the assistant message grows in the conversation region until the response completes

### Requirement: Running phase indicator

The TUI SHALL track and expose the current run phase: `idle`, `running`, or `awaiting_approval`. Internally, the phase SHALL be represented by a `RunPhase` enumeration whose values match these strings for footer and `/status` display.

#### Scenario: Phase during tool execution

- **WHEN** the agent is executing tools for a user task
- **THEN** the run phase is `running` until the final assistant reply is shown

#### Scenario: Phase during approval

- **WHEN** the agent waits for user approval of a confirm-tier operation
- **THEN** the run phase is `awaiting_approval`

#### Scenario: Phase returns to idle after task

- **WHEN** an agent task completes or fails with an error shown in the conversation
- **THEN** the run phase is `idle`

### Requirement: In-TUI system output

Slash-command output, agent step progress, tool calls, tool results, permission rejections, and non-fatal errors during interactive use SHALL be rendered in the conversation region rather than interleaved on stderr.

#### Scenario: Step progress in conversation

- **WHEN** the agent executes tool calls during a task in TUI mode
- **THEN** brief step summaries appear in the conversation region as system notices

#### Scenario: Tool result in conversation

- **WHEN** a tool returns output during a TUI task
- **THEN** a truncated tool result summary appears in the conversation region

#### Scenario: Error in conversation

- **WHEN** a task fails with `LLMError` during TUI mode
- **THEN** an error message appears in the conversation region and the TUI remains usable for further input

### Requirement: Status footer

The TUI SHALL display a footer showing the active model and working directory path for the session.

#### Scenario: Footer reflects session state

- **WHEN** the user switches model via `/model <id>` in TUI mode
- **THEN** the footer updates to show the new active model

#### Scenario: Footer shows working directory

- **WHEN** the TUI is running
- **THEN** the footer includes the resolved working directory path

### Requirement: TUI exit

The TUI SHALL exit gracefully when the user submits `exit`, uses an agreed quit shortcut, or interrupts with Ctrl+C.

#### Scenario: Exit keyword

- **WHEN** the user submits `exit` at the TUI input
- **THEN** the application exits with code 0

### Requirement: Restore conversation on resume

When interactive mode starts with a resumed session, the TUI SHALL populate the conversation region with all saved display messages before accepting new input.

#### Scenario: TUI shows prior turns after resume

- **WHEN** the user runs `coding-agent --resume <id>` and the session file contains prior user and assistant messages
- **THEN** the TUI conversation region shows those messages in chronological order on launch

#### Scenario: Resume mid-session via slash command

- **WHEN** the user types `/resume <id>` in the TUI
- **THEN** the conversation region clears and repopulates from the loaded session

### Requirement: Session id in TUI footer

The TUI footer SHALL include the current session's short id alongside the active model and working directory.

#### Scenario: Footer shows session id

- **WHEN** the TUI is running with session id `abc123`
- **THEN** the footer includes a short form of `abc123` with model and working directory

#### Scenario: Footer updates on new session

- **WHEN** the user types `/new` in the TUI
- **THEN** the footer updates to show the new session id
