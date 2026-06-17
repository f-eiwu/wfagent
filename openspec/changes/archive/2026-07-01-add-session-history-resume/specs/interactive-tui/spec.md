## ADDED Requirements

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
