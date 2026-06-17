## ADDED Requirements

### Requirement: Display history includes tool events

Persisted session display messages SHALL include tool call summaries, tool result summaries, and permission rejection notices shown during interactive runs.

#### Scenario: Tool events restored on resume

- **WHEN** the user resumes a session that recorded tool call and result system messages
- **THEN** the TUI conversation region shows those messages in chronological order

#### Scenario: Rejection persisted in display history

- **WHEN** the user rejects a confirm-tier operation during an interactive task
- **THEN** the rejection notice is saved in `display_messages` with the session file
