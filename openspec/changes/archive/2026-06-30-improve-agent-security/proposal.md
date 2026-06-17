## Why

The coding agent can read/write files and run arbitrary shell commands in the user's working directory with no guardrails beyond basic path traversal checks. A mistaken or malicious LLM tool call could delete files, exfiltrate secrets, or run destructive commands. Hardening tool execution and adding user confirmation reduces blast radius while keeping the agent useful for normal coding tasks.

## What Changes

- **BREAKING**: Disable `run_shell` by default; require `--allow-shell` to enable it
- Add a shell command blocklist rejecting obviously dangerous patterns (`rm -rf`, `curl | sh`, disk format, etc.)
- Add symlink-safe path resolution so file tools cannot follow links outside the working directory
- Block read/write of sensitive file patterns (`.env`, `*.pem`, `*credentials*`, etc.)
- Add interactive confirmation before destructive operations (shell commands and file overwrites), skippable with `--yes`
- Redact likely secrets (API keys, tokens) from tool output returned to the LLM
- Update README with security model and new flags

## Capabilities

### New Capabilities

- `shell-policy`: Shell tool gating, dangerous-command blocklist, and safe execution constraints
- `confirmation-gate`: User approval flow for destructive tool calls before execution

### Modified Capabilities

- `coding-tools`: Symlink-safe path resolution, sensitive-file denylist, output redaction on file reads
- `cli`: New `--allow-shell` and `--yes` flags; security warnings on startup

## Impact

- **Code**: `shell_tools.py`, `file_tools.py`, new `security/` module, `agent.py`, `cli.py`, `config.py`
- **CLI**: Breaking change for scripts that rely on shell tool without `--allow-shell`
- **Tests**: New security-focused test suite
- **Docs**: README security section expanded
