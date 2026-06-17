## ADDED Requirements

### Requirement: Session-scoped conversation across interactive turns

In interactive mode, the agent SHALL reuse LLM message history (system, user, assistant, tool) across follow-up tasks within the same session so later tasks can reference earlier context.

#### Scenario: Follow-up sees prior task context

- **WHEN** the user asks "create foo.py" and then submits "now add tests for it" in the same session
- **THEN** the second agent run includes messages from the first task in the LLM conversation

#### Scenario: New session clears agent history

- **WHEN** the user starts a `/new` session or resumes a different session id
- **THEN** the agent's in-memory message list matches the loaded session file (not prior in-memory turns)

#### Scenario: One-shot task remains isolated

- **WHEN** the user runs `coding-agent --task "hello"`
- **THEN** the agent uses only messages for that single task and does not read or write session files
