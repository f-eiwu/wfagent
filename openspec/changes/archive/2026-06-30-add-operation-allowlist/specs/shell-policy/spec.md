## MODIFIED Requirements

### Requirement: Shell tool opt-in

The agent SHALL register and expose the `run_shell` tool by default. Shell execution SHALL be subject to the dangerous-command blocklist and confirm-tier user approval via the session operation allowlist.

#### Scenario: Shell available by default

- **WHEN** the agent starts with default configuration
- **THEN** the `run_shell` tool is registered and available to the LLM

#### Scenario: Shell requires approval

- **WHEN** the LLM requests `run_shell` and the command is not on the session allowlist
- **THEN** the agent prompts for user confirmation before executing
