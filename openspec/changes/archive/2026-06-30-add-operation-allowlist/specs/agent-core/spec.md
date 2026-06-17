## ADDED Requirements

### Requirement: Tool execution uses operation allowlist

Before dispatching a tool call, the agent SHALL consult the session operation allowlist and confirmation policy. Auto-tier tools dispatch immediately; confirm-tier tools require approval or a matching allowlist entry.

#### Scenario: Agent checks allowlist before write

- **WHEN** the LLM requests `write_file` and the path is not allowlisted
- **THEN** the agent prompts for confirmation before calling the tool implementation

#### Scenario: Agent passes rejection to LLM on deny

- **WHEN** the user rejects a confirm-tier tool call
- **THEN** the agent appends a tool result describing the rejection and continues the step loop
