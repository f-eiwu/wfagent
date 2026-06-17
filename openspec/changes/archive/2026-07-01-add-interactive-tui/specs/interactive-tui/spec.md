## ADDED Requirements

### Requirement: Full-screen interactive layout

When interactive mode runs on a TTY without plain mode, the CLI SHALL present a full-screen terminal UI with a header region, scrollable conversation region, bottom input region, and status footer.

#### Scenario: TUI launches on interactive start

- **WHEN** the user runs `coding-agent` on a TTY without `--task` and without plain mode enabled
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

### Requirement: In-TUI system output

Slash-command output, agent step progress, and non-fatal errors during interactive use SHALL be rendered in the conversation region rather than interleaved on stderr.

#### Scenario: Step progress in conversation

- **WHEN** the agent executes tool calls during a task in TUI mode
- **THEN** brief step summaries appear in the conversation region as system notices

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
