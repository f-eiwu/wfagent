## Context

The agent already satisfies much of the L1 brief: TUI, agent loop, read/write/list/shell tools, operation allowlist, LLM provider defaults, session persistence, and slash commands. A requirements audit against `project_requirements.pdf` identified concrete gaps: no `glob`/`grep`/`edit` tools, no user/project config files, TUI does not show tool results or rejections in conversation, no `/status`, LLM streaming is internal-only (not shown to user), no LLM timeout/retry config, and main specs omit `--yes`/`-y` though code supports it.

Constraints from the brief: custom agent loop (no Agent SDK), TUI mandatory, permission control with rejection in session context, API keys must not leak.

## Goals / Non-Goals

**Goals:**

- Close all **functional** gaps in Section 二–三 of the L1 requirements PDF
- Add **layered config** (user + project TOML; project wins over user; CLI/env win over files)
- Add **`glob_files`**, **`search_code`**, **`edit_file`** tools (edit is confirm-tier)
- Show **tool calls, results, rejections** in TUI and persist in session display history
- **Stream** assistant tokens to TUI during generation
- **LLM timeout** and **basic retry** (transient API errors)
- Add **`/status`** built-in command
- **Retain `--yes`/`-y`** as global auto-approve bypass (convenience for scripts)
- Add tests for **config priority** and expanded mock-LLM coverage

**Non-Goals:**

- Full IDE-style diff UI or patch preview modals
- Context compression / subagents / MCP plugins
- Persistent deny-list across sessions
- Replacing TOML with YAML or JSON
- Sandboxed/container execution

## Decisions

### 1. Config file format and locations

**Decision:** TOML files, stdlib-only parser via `tomllib` (Python 3.11+).

| Layer | Path |
|-------|------|
| User | `~/.config/coding-agent/config.toml` (Windows: `%APPDATA%/coding-agent/config.toml`) |
| Project | `<working_dir>/.coding-agent.toml` |

**Merge order (lowest → highest priority):** hardcoded defaults → user file → project file → environment variables → CLI flags.

**Fields in files:** `model`, `base_url`, `max_steps`, `request_timeout` (seconds). **Not in files:** `api_key` (env `OPENAI_API_KEY` or `--api-key` only).

**Rationale:** Matches L1 “user + project config, project overrides user”; TOML is readable and has no new dependency.

### 2. New repository tools

| Tool | Tier | Implementation |
|------|------|----------------|
| `glob_files` | Auto | `pathlib.Path.glob` under safe resolved directory |
| `search_code` | Auto | Walk tree under cwd; regex or fixed-string match; cap matches (e.g. 100) |
| `edit_file` | Confirm | Read file, replace `old_string` with `new_string` once; error if not found or ambiguous |

**Rationale:** Directly maps to 文件匹配 / 内容搜索 / 文件编辑 in the brief without shell fallbacks.

### 3. Tool visibility in TUI and session

**Decision:** Extend `Agent.run()` with optional callbacks:

- `on_tool_call(name, arguments_summary)`
- `on_tool_result(name, result_summary)` — truncate long output (e.g. 500 chars)
- `on_tool_rejected(name, reason)`

TUI appends **system** messages with clear prefixes: `Tool call:`, `Tool result:`, `Rejected:`.

`SessionState.display_messages` records the same lines so resume restores full audit trail.

**Rationale:** Satisfies “展示工具调用过程、工具执行结果、权限拒绝结果” without new TUI widget types in v1.

### 4. LLM streaming, timeout, retry

**Decision:**

- Add `request_timeout` to `Config` (default 120s), passed to LLM provider client
- On `APIError` or timeout: retry up to 2 times with 1s backoff
- When streaming: invoke `on_stream_chunk(text)` for each content delta; TUI updates a live assistant message widget (append mode)

Non-streaming path unchanged for providers that don't stream.

**Rationale:** Covers 流式输出、超时控制、基础重试 without rewriting the agent loop.

### 5. `--yes`/`-y` retention

**Decision:** Keep `Config.auto_approve` and CLI `--yes`/`-y`. Document as explicit bypass of confirm-tier prompts (allowlist still not required when `-y` is set). Specs updated to reflect this—differs from archived allowlist proposal but matches user intent and current code.

**Rationale:** User-requested convenience; L1 requires confirmation by default in interactive mode, not a ban on automation flags.

### 6. `/status` command

**Decision:** New slash command prints (TUI: system message; plain: stderr):

- session id, model, working dir, max_steps, base_url (no api key), `auto_approve` flag state, current phase (`idle` / `running` / `awaiting_approval`)

Track phase in TUI `CodingAgentApp` fields.

### 7. Tests

Add `tests/test_config_files.py` for merge priority. Extend `test_agent.py` / `test_tui_app.py` for tool event display and rejection in history. Mock LLM already used; add streaming callback test in `test_llm.py`.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Large tool output floods TUI | Truncate result summaries; full content stays in `agent_messages` |
| `edit_file` ambiguous replace | Require unique `old_string` or return error |
| Config file secrets | Reject `api_key` key in TOML with clear error |
| Streaming + tool calls in one response | Existing stream parser already accumulates tool_calls |
| Spec drift on `--yes` | Update `cli` and `operation-allowlist` delta specs in this change |

## Migration Plan

1. Ship new tools and config loader (backward compatible: no config files = current behavior)
2. Update TUI/agent callbacks (additive)
3. Update README with config paths, new tools, `/status`, LLM provider defaults
4. No session file format version bump required (display messages are append-only strings)

## Open Questions

- Use regex by default for `search_code` or offer `fixed_string` param? **Recommend:** `pattern` + optional `fixed_string: bool` default false.
- Windows user config path: use `%APPDATA%/coding-agent/config.toml` — confirm in implementation.
