## MODIFIED Requirements

### Requirement: Configuration flags

The CLI SHALL accept flags for LLM configuration: `--api-key`, `--model`, `--base-url`, and `--max-steps`. Security is enforced via the operation allowlist (auto reads; confirmed writes and shell), not via `--allow-shell` or `--yes`.

#### Scenario: Override model via flag

- **WHEN** the user runs `coding-agent --model gpt-4o --task "explain this codebase"`
- **THEN** the agent uses `gpt-4o` for LLM calls

## REMOVED Requirements

### Requirement: Allow shell flag

**Reason**: Shell is always registered; risky operations use confirm-tier approval instead of opt-in registration.

**Migration**: Remove `--allow-shell` from scripts; approve shell commands interactively when prompted.

### Requirement: Auto-approve flag

**Reason**: Global confirmation bypass removed in favor of session operation allowlist.

**Migration**: Remove `--yes` from scripts; run interactively or use read-only operations in non-TTY mode.

### Requirement: Security warning on startup

**Reason**: No longer tied to removed `--allow-shell` and `--yes` flags.

**Migration**: Security model documented in README under operation allowlist.
