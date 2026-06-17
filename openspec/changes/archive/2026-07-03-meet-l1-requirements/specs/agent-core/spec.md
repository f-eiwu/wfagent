## ADDED Requirements

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
