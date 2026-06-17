## MODIFIED Requirements

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
