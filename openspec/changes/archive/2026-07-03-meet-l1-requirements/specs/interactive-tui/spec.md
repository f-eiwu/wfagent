## ADDED Requirements

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

The TUI SHALL track and expose the current run phase: `idle`, `running`, or `awaiting_approval`.

#### Scenario: Phase during tool execution

- **WHEN** the agent is executing tools for a user task
- **THEN** the run phase is `running` until the final assistant reply is shown

#### Scenario: Phase during approval

- **WHEN** the agent waits for user approval of a confirm-tier operation
- **THEN** the run phase is `awaiting_approval`

## MODIFIED Requirements

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
