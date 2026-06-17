## ADDED Requirements

### Requirement: Tool risk classification

The system SHALL classify agent tools into auto and confirm tiers. Auto-tier tools execute without user approval. Confirm-tier tools require user approval before first execution in a session unless already on the session allowlist.

#### Scenario: Auto-tier read operations

- **WHEN** the LLM requests `read_file` or `list_dir`
- **THEN** the agent executes the tool immediately without a confirmation prompt

#### Scenario: Confirm-tier write operations

- **WHEN** the LLM requests `write_file` and the operation is not on the session allowlist
- **THEN** the agent prompts the user for approval before executing

#### Scenario: Confirm-tier shell operations

- **WHEN** the LLM requests `run_shell` and the command is not on the session allowlist
- **THEN** the agent prompts the user for approval before executing

### Requirement: Session operation allowlist

The system SHALL maintain a session-scoped allowlist of approved confirm-tier operations. An approved operation MAY execute again in the same session without re-prompting.

#### Scenario: Approve and remember write path

- **WHEN** the user approves `write_file` for path `src/foo.py`
- **THEN** subsequent `write_file` calls to `src/foo.py` in the same session execute without prompting

#### Scenario: Approve and remember shell command

- **WHEN** the user approves `run_shell` with command `pytest`
- **THEN** subsequent `run_shell` with command `pytest` in the same session execute without prompting

#### Scenario: Different operations require separate approval

- **WHEN** the user approved `write_file` for `a.py` but the LLM requests `write_file` for `b.py`
- **THEN** the agent prompts for approval before executing `b.py`

#### Scenario: New session clears allowlist

- **WHEN** the user starts a `/new` session or begins a fresh interactive session
- **THEN** the operation allowlist is empty

### Requirement: Rejection returns message to LLM

When the user rejects a confirm-tier operation, the agent SHALL skip execution and return a rejection message to the LLM as the tool result.

#### Scenario: User rejects write

- **WHEN** the user responds with anything other than `y` or `yes` at the approval prompt for `write_file`
- **THEN** the tool is not executed and the LLM receives a rejection message

### Requirement: Non-interactive mode rejects confirm-tier operations

When stdin is not a TTY and the operation is not on the allowlist, the agent SHALL reject confirm-tier tool calls without executing them.

#### Scenario: One-shot task with write on non-TTY

- **WHEN** the user runs `coding-agent --task "edit foo.py"` without a TTY and `write_file` is requested
- **THEN** the tool call is rejected with an error indicating interactive confirmation is required
