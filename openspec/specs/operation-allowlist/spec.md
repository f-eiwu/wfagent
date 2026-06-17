## Purpose

Session-scoped risk tiers and operation allowlist for confirm-tier tools.

## Requirements

### Requirement: Tool risk classification

The system SHALL classify agent tools into auto and confirm tiers. Auto-tier tools execute without user approval. Confirm-tier tools require user approval before first execution in a session unless already on the session allowlist or global auto-approve (`--yes`/`-y`) is enabled.

#### Scenario: Auto-tier read operations

- **WHEN** the LLM requests `read_file`, `list_dir`, `glob_files`, or `search_code`
- **THEN** the agent executes the tool immediately without a confirmation prompt

#### Scenario: Confirm-tier write operations

- **WHEN** the LLM requests `write_file` or `edit_file` and the operation is not on the session allowlist and auto-approve is false
- **THEN** the agent prompts the user for approval before executing

#### Scenario: Confirm-tier shell operations

- **WHEN** the LLM requests `run_shell` and the command is not on the session allowlist and auto-approve is false
- **THEN** the agent prompts the user for approval before executing

#### Scenario: Auto-approve bypasses confirmation

- **WHEN** the user started the agent with `--yes`/`-y` and the LLM requests a confirm-tier tool
- **THEN** the agent executes without prompting (allowlist entry is not required)

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

#### Scenario: Non-TTY interactive with write and no auto-approve

- **WHEN** the user runs `coding-agent` without a TTY (no `--yes`) and submits a task that requests `write_file`
- **THEN** the tool call is rejected with an error indicating interactive confirmation is required
