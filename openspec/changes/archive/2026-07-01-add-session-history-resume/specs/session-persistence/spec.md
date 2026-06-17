## ADDED Requirements

### Requirement: Session files stored on disk

The system SHALL persist interactive session state as JSON files under `.ai_history/sessions/` in the project working directory (or a configurable sessions root derived from `working_dir`). Each file SHALL be named by a unique session id.

#### Scenario: New session creates a file

- **WHEN** the user starts interactive mode without `--resume` or `--continue`
- **THEN** the system creates a new session id and writes an initial session file under `.ai_history/sessions/`

#### Scenario: Session file includes required fields

- **WHEN** a session is saved
- **THEN** the file contains session id, title, created and updated timestamps, active model, working directory path, display messages, and LLM message history

### Requirement: Auto-save on interactive turns

The system SHALL save the current session to disk after each completed interactive turn (task or slash command that mutates session state) and on graceful exit (`exit`, Ctrl+C, or TUI quit).

#### Scenario: Save after agent task

- **WHEN** the user submits a task in interactive mode and the agent returns a final response
- **THEN** the session file is updated with the new messages and timestamp

#### Scenario: Save on exit

- **WHEN** the user exits interactive mode gracefully
- **THEN** the session file is written one final time before the process exits

### Requirement: List saved sessions

The system SHALL list saved sessions for the current working directory, ordered by most recently updated first.

#### Scenario: Sessions slash command

- **WHEN** the user types `/sessions` in interactive mode
- **THEN** the CLI prints each session's short id, title, last-updated time, and active model

#### Scenario: Empty session list

- **WHEN** the user types `/sessions` and no session files exist for the working directory
- **THEN** the CLI reports that no saved sessions were found

### Requirement: Resume session by id

The system SHALL restore session state from a saved session file when given a valid session id.

#### Scenario: Resume via CLI flag

- **WHEN** the user runs `coding-agent --resume <id>` without `--task`
- **THEN** the CLI loads the session file, restores model, messages, and LLM history, and enters interactive mode

#### Scenario: Resume via slash command

- **WHEN** the user types `/resume <id>` during an interactive session
- **THEN** the CLI loads that session, replaces current session state, and continues interactively

#### Scenario: Invalid session id

- **WHEN** the user provides a session id that does not exist for the working directory
- **THEN** the CLI prints an error and does not change state (or does not start, for CLI flag)

### Requirement: Continue most recent session

The system SHALL support resuming the most recently updated session for the working directory.

#### Scenario: Continue flag

- **WHEN** the user runs `coding-agent --continue` without `--task`
- **THEN** the CLI loads the latest session file for the working directory and enters interactive mode with restored state

#### Scenario: No session to continue

- **WHEN** the user runs `coding-agent --continue` and no session files exist
- **THEN** the CLI starts a new session and informs the user that no prior session was found

### Requirement: Start new session

The system SHALL allow the user to discard the in-memory session and begin a fresh session without exiting interactive mode.

#### Scenario: New session slash command

- **WHEN** the user types `/new` in interactive mode
- **THEN** the CLI clears conversation and LLM history, assigns a new session id, and saves a fresh session file

### Requirement: Session title from first task

The system SHALL set the session title from the first user-submitted task text (truncated to a reasonable length). Slash commands and empty input SHALL NOT change an existing title.

#### Scenario: Title set on first task

- **WHEN** the user's first submitted line in a new session is `fix the login bug`
- **THEN** the saved session title reflects that text (truncated if long)

### Requirement: One-shot mode does not persist sessions

The system SHALL NOT create or update session files when running with `--task`.

#### Scenario: One-shot task

- **WHEN** the user runs `coding-agent --task "hello"`
- **THEN** no session file is written under `.ai_history/sessions/`
