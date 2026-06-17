## ADDED Requirements

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
