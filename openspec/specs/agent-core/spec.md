## Purpose

Core agent loop, conversation management, and LLM integration.

## Requirements

### Requirement: Agent executes a task via LLM tool-calling loop

The agent SHALL accept a user task (natural-language string) and execute it by repeatedly calling the LLM with the conversation history and available tool definitions until the LLM returns a final text response with no tool calls, or the step limit is reached.

#### Scenario: Task completes in one step

- **WHEN** the user provides a task that the LLM can answer without tools
- **THEN** the agent returns the LLM's text response and exits with success

#### Scenario: Task requires tool use

- **WHEN** the user provides a task that requires reading or writing files
- **THEN** the agent executes the requested tool calls, appends results to the conversation, and calls the LLM again

#### Scenario: Step limit reached

- **WHEN** the agent has executed `max_steps` iterations without a final answer
- **THEN** the agent stops and reports that the step limit was reached

### Requirement: Agent maintains conversation history

The agent SHALL maintain a message list (system, user, assistant, tool) that grows with each LLM call and tool execution within a single run.

#### Scenario: Tool results are fed back to LLM

- **WHEN** the LLM requests a tool call and the tool returns a result
- **THEN** the agent appends an assistant message with the tool call and a tool message with the result before the next LLM call

### Requirement: Agent uses a system prompt

The agent SHALL prepend a system message describing its role as a coding assistant, the available tools, and the working directory path.

#### Scenario: System prompt includes working directory

- **WHEN** the agent starts with working directory `/home/user/project`
- **THEN** the system prompt informs the LLM that file paths are relative to `/home/user/project`

### Requirement: Configurable step limit

The agent SHALL accept a `max_steps` parameter (integer, default 20) that limits the number of LLM call iterations.

#### Scenario: Custom step limit

- **WHEN** `max_steps` is set to 5 and the task requires more than 5 iterations
- **THEN** the agent stops after 5 steps and reports the limit was reached

### Requirement: LLM provider configuration

The agent SHALL connect to an LLM using configurable API key, model name, and base URL, resolved from environment variables or CLI flags.

#### Scenario: Missing API key

- **WHEN** no API key is provided via environment or CLI
- **THEN** the agent exits with a clear error message before making any LLM call

### Requirement: Session-scoped conversation across interactive turns

In interactive mode, the agent SHALL reuse LLM message history (system, user, assistant, tool) across follow-up tasks within the same session so later tasks can reference earlier context.

#### Scenario: Follow-up sees prior task context

- **WHEN** the user asks "create foo.py" and then submits "now add tests for it" in the same session
- **THEN** the second agent run includes messages from the first task in the LLM conversation

#### Scenario: New session clears agent history

- **WHEN** the user starts a `/new` session or resumes a different session id
- **THEN** the agent's in-memory message list matches the loaded session file (not prior in-memory turns)

### Requirement: Tool execution uses operation allowlist

Before dispatching a tool call, the agent SHALL consult the session operation allowlist and confirmation policy. Auto-tier tools dispatch immediately; confirm-tier tools require approval or a matching allowlist entry.

#### Scenario: Agent checks allowlist before write

- **WHEN** the LLM requests `write_file` and the path is not allowlisted
- **THEN** the agent prompts for confirmation before calling the tool implementation

#### Scenario: Agent passes rejection to LLM on deny

- **WHEN** the user rejects a confirm-tier tool call
- **THEN** the agent appends a tool result describing the rejection and continues the step loop

### Requirement: LLM request timeout

The agent SHALL apply a configurable HTTP timeout to LLM API requests.

#### Scenario: Timeout from configuration

- **WHEN** `request_timeout` is set to 60 seconds and the API does not respond in time
- **THEN** the agent surfaces an `LLMError` indicating the request timed out

### Requirement: LLM transient retry

The LLM client SHALL retry failed API requests up to 2 times on transient errors (timeouts, 5xx, connection errors) with a short backoff before surfacing failure.

#### Scenario: Retry succeeds on second attempt

- **WHEN** the first API call fails with a transient error and the second succeeds
- **THEN** the agent receives the completion without user-visible failure

#### Scenario: Retries exhausted

- **WHEN** all retry attempts fail
- **THEN** the agent surfaces an `LLMError` with the last error message

### Requirement: Streaming callback for assistant content

The agent SHALL support an optional callback invoked with assistant content chunks when the LLM response is streamed, so the UI can render incremental output.

#### Scenario: Stream chunks delivered

- **WHEN** streaming is active and the LLM emits content deltas
- **THEN** each non-empty content delta is passed to the registered callback in order

### Requirement: Tool event callbacks

The agent SHALL support optional callbacks for tool call, tool result, and rejection events so interactive UIs can render execution visibility.

#### Scenario: Tool call callback

- **WHEN** the LLM requests a tool and the agent is about to execute or approve it
- **THEN** an `on_tool_call` callback receives the tool name and argument summary

#### Scenario: Tool result callback

- **WHEN** a tool finishes execution
- **THEN** an `on_tool_result` callback receives the tool name and a truncated result summary

#### Scenario: Rejection callback

- **WHEN** the user rejects a confirm-tier operation
- **THEN** an `on_tool_rejected` callback receives the tool name and rejection reason

### Requirement: Agent progress logging

When no step callback is registered, the agent SHALL emit step progress (`thinking`, tool names) through the operational logger at INFO level instead of `print`.

#### Scenario: Headless agent run logs steps

- **WHEN** `Agent.run` executes without `on_step`
- **THEN** each step summary is logged at INFO under the agent module logger

#### Scenario: Interactive run avoids duplicate logs

- **WHEN** `Agent.run` executes with `on_step` provided
- **THEN** step summaries are not also logged at INFO by the agent
