## 1. Layered configuration

- [x] 1.1 Create `src/coding_agent/config_files.py` — load user and project TOML, reject `api_key` in files
- [x] 1.2 Extend `Config.from_sources()` merge order: defaults → user file → project file → env → CLI; add `request_timeout`
- [x] 1.3 Add `tests/test_config_files.py` for project-over-user, CLI-over-file, and api_key rejection

## 2. Repository tools

- [x] 2.1 Implement `glob_files` in file tools with path safety and match limits
- [x] 2.2 Implement `search_code` with regex/fixed-string, match cap, and redaction on snippets
- [x] 2.3 Implement `edit_file` (unique replace) as confirm-tier in `operation_allowlist.py`
- [x] 2.4 Register new tools in `create_default_registry()` and update confirmation summaries
- [x] 2.5 Add tool tests in `tests/test_tools.py` for glob, search, and edit (happy path + errors)

## 3. LLM timeout, retry, and streaming

- [x] 3.1 Pass `request_timeout` to LLM provider client in `llm.py`
- [x] 3.2 Add transient retry (max 2) with backoff on API failures
- [x] 3.3 Add optional `on_stream_chunk` callback to `LLMClient.chat()` / stream parser
- [x] 3.4 Extend `tests/test_llm.py` for retry and stream callback behavior

## 4. Agent tool events and UI hooks

- [x] 4.1 Add `on_tool_call`, `on_tool_result`, `on_tool_rejected` callbacks to `Agent.run()`
- [x] 4.2 Truncate tool result summaries for display (e.g. 500 chars)
- [x] 4.3 Wire callbacks in plain interactive loop (`cli.py`) to stderr system lines
- [x] 4.4 Wire callbacks + streaming in `tui/app.py`; track run phase (`idle`/`running`/`awaiting_approval`)
- [x] 4.5 Persist tool event system messages in `display_messages` via session sync

## 5. Slash commands and CLI

- [x] 5.1 Add `/status` to `slash_commands.py` and help text
- [x] 5.2 Verify `--yes`/`-y` remains on all entry points; document in README
- [x] 5.3 Update interactive startup hint to mention `/status`
- [x] 5.4 Add `tests/test_slash_commands.py` and `tests/test_tui_app.py` coverage for `/status`

## 6. Tests and documentation

- [x] 6.1 Add agent test: rejection message in tool history and rejection callback fired
- [x] 6.2 Add TUI test: tool call/result lines appear in conversation
- [x] 6.3 Update README: layered config paths, new tools, `/status`, LLM provider defaults, `--yes`/`-y`
- [x] 6.4 Run full `pytest` suite and fix regressions
