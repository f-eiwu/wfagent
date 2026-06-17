# Coding Agent

A TUI terminal coding AI agent that accepts natural-language tasks, calls an LLM with tool definitions, and executes file and shell operations to complete them. Defaults to the chat-completions API.

## Requirements

- Python 3.11+
- A chat-completions-compatible API key (any compatible provider)

## Installation

```bash
pip install -e .
```

For development (includes pytest):

```bash
pip install -e ".[dev]"
```

## Configuration

Settings resolve in this order (lowest to highest priority):

1. Built-in defaults
2. User config file (`~/.config/coding-agent/config.toml`, or `%APPDATA%/coding-agent/config.toml` on Windows)
3. Project config file (`.coding-agent.toml` in the working directory)
4. Environment variables
5. CLI flags

API keys are **never** read from config files — use `OPENAI_API_KEY` or `--api-key` only.

| Setting | CLI flag | Environment variable | Config file key | Default |
|---------|----------|---------------------|-----------------|---------|
| API key | `--api-key` | `OPENAI_API_KEY` | — | (required) |
| Model | `--model` | `OPENAI_MODEL` | `model` | `gpt-4o-mini` |
| Base URL | `--base-url` | `OPENAI_BASE_URL` | `base_url` | `https://api.openai.com/v1` |
| Max steps | `--max-steps` | `CODING_AGENT_MAX_STEPS` | `max_steps` | `20` |
| LLM timeout | — | `CODING_AGENT_REQUEST_TIMEOUT` | `request_timeout` | `120` (seconds) |
| Log level | `--log-level` | `CODING_AGENT_LOG_LEVEL` | `log_level` | `INFO` |
| Working dir | `--cwd` | — | — | current directory |
| Auto-approve | `--yes`, `-y` | — | — | disabled |

Example `.coding-agent.toml`:

```toml
model = "gpt-4o-mini"
max_steps = 30
request_timeout = 90
log_level = "DEBUG"
```

## Usage

Start the interactive TUI (default on a TTY):

```bash
coding-agent
```

Files are created under the current directory by default. Override with `--cwd` (e.g. `--cwd deliverables`).

### Operation allowlist

Read-only tools (`read_file`, `list_dir`, `glob_files`, `search_code`) run automatically. Writes, edits, and shell commands require approval the first time each path or command is used in a session (unless `--yes`/`-y`). Approved operations are remembered for the session and saved on disk.

```bash
coding-agent -y
```

### Interactive modes

On a TTY, `coding-agent` launches a **full-screen TUI**: conversation history (including tool calls, results, and approvals), follow-up input, and a status footer.

Plain text mode (no full-screen TUI):

```bash
coding-agent --plain
```

Slash commands (TUI and plain):

```text
/help
/status
/model
/model gpt-4o
/sessions
/resume <session-id>
/new
/clear
/rm <session-id>
```

`/status` shows session id, model, working directory, limits, and current run phase.

### Session management

```bash
coding-agent ls
coding-agent resume
coding-agent --continue
coding-agent --resume <session-id>
```

Sessions are stored under `.ai_history/sessions/`.

## Available Tools

- `read_file` — read file contents (truncated at 500 lines, secrets redacted)
- `write_file` — create or overwrite files (confirm-tier)
- `edit_file` — replace a unique string in a file (confirm-tier)
- `list_dir` — list directory contents
- `glob_files` — find files by glob pattern
- `search_code` — search file contents by regex or fixed string
- `run_shell` — execute shell commands (confirm-tier)

## Security

- **Operation allowlist** — reads/search auto-run; writes/edits/shell prompt once per path/command per session
- **`--yes`/`-y`** — bypass confirm-tier prompts (scripts and non-TTY one-shot)
- **Command blocklist** — blocks dangerous shell patterns
- **Path protection** — rejects traversal and symlink escapes
- **Sensitive file denylist** — blocks `.env`, `*.pem`, etc.
- **Output redaction** — secrets scrubbed from tool output

## Development

```bash
pytest
```

### Session log hygiene

When updating collaboration exports under `.ai_history/logs/`, redact secret values before committing:

```bash
python -c "from pathlib import Path; from coding_agent.security.redaction import anonymize_logs_dir; print(anonymize_logs_dir(Path('.ai_history/logs')))"
```

## License

MIT
