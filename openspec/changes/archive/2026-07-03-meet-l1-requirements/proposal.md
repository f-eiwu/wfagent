## Why

The L1 certification task (`project_requirements.pdf`) defines a minimum TUI coding agent with repository tools, permission control, LLM provider integration, layered configuration, and rich session/TUI visibility. The current agent implements the core loop, allowlist security, sessions, and TUI, but gaps remain against the official requirements—especially search/glob/edit tools, user+project config, tool-result visibility in the TUI, LLM streaming/timeout/retry, and the `/status` built-in command. This change closes those gaps while **keeping `--yes`/`-y`** as a convenience bypass for non-interactive and scripted use.

## What Changes

- Add **`glob_files`** (file matching) and **`search_code`** (content search) tools; add **`edit_file`** for in-place edits (confirm-tier, like writes)
- Add **layered configuration**: user-level file + project-level file; project overrides user; CLI flags override both; API keys never written to config files
- Surface **tool call arguments, tool results, and permission rejections** in TUI conversation and persisted session display history
- Add **`/status`** slash command showing session id, model, cwd, step limit, provider URL, and current run phase
- Enhance **LLM client**: stream assistant tokens to TUI/plain progress, configurable request timeout, basic retry on transient API failures
- Update **tests** for config priority, tool result display, new tools, and mock LLM scenarios per delivery checklist
- **Retain `--yes`/`-y`**: auto-approve confirm-tier operations (document in specs; does not weaken default interactive approval)
- Align **README** defaults with chat-completions-compatible (`gpt-4o-mini`, provider base URL)

## Capabilities

### New Capabilities

- `layered-config`: User-level and project-level TOML config files with project-over-user priority; covers provider, model, base URL, timeout, max steps

### Modified Capabilities

- `coding-tools`: Add `glob_files`, `search_code`, `edit_file` tools
- `interactive-tui`: Show tool calls, tool results, rejections; stream assistant output; running-state indicators
- `cli`: Add `/status`; document `--yes`/`-y`; integrate layered config resolution
- `agent-core`: LLM streaming callbacks, timeout, retry; emit structured tool events for UI
- `session-persistence`: Persist tool-call and tool-result lines in display history
- `operation-allowlist`: Document `--yes`/`-y` as explicit auto-approve bypass alongside session allowlist

## Impact

- `src/coding_agent/tools/` — new search/glob/edit tools and factory registration
- New `src/coding_agent/config_files.py` (or similar) — load/merge user + project config
- `src/coding_agent/config.py` — merge layered config; add `request_timeout`
- `src/coding_agent/llm.py` — timeout, retry, streaming callback hook
- `src/coding_agent/agent.py` — tool event callbacks for UI; pass streaming hook
- `src/coding_agent/tui/app.py` — render tool calls/results/rejections; incremental assistant text
- `src/coding_agent/slash_commands.py` — `/status`
- `src/coding_agent/cli.py` — config resolution order; keep `-y`/`--yes`
- `tests/` — new and updated tests per delivery requirements
- `README.md` — config files, new tools, `/status`, LLM provider defaults
