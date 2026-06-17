## Why

Interactive sessions today are ephemeral: quitting the CLI or TUI discards the conversation log, input context, and LLM message history. Each follow-up task also starts a fresh agent with no memory of prior turns. modern coding agent persists sessions locally so users can close the terminal and continue later with full context. Saving and resuming sessions makes multi-day coding tasks practical and matches user expectations from modern agent UIs.

## What Changes

- Persist interactive session state to disk under `.ai_history/sessions/` (metadata, display messages, LLM conversation history, active model, working directory)
- Auto-save after each interactive turn and on graceful exit
- Add `--resume <id>` and `--continue` CLI flags to restore a prior session on startup
- Add slash commands `/sessions`, `/resume <id>`, and `/new` in interactive mode (TUI and plain)
- Carry LLM conversation history across follow-up tasks within a session so the agent remembers prior turns
- Restore TUI conversation scrollback and plain-mode context when resuming
- Show session id (short form) in the TUI footer and plain-mode status line
- One-shot `--task` mode remains unchanged (no session file created)

## Capabilities

### New Capabilities

- `session-persistence`: On-disk session storage, listing, auto-save, resume, and session lifecycle (`/new`, `/resume`)

### Modified Capabilities

- `cli`: `--resume` / `--continue` flags; session slash commands; startup behavior when resuming
- `agent-core`: Session-scoped LLM message history reused across interactive follow-up tasks
- `interactive-tui`: Restore conversation on resume; reflect session id in footer; persist display messages

## Impact

- New `src/coding_agent/session_store.py` (or similar) — load/save/list session files
- `src/coding_agent/session.py` — extend `SessionState` with id, agent messages, display messages
- `src/coding_agent/agent.py` — accept optional initial messages; expose messages after run for persistence
- `src/coding_agent/cli.py` — resume flags, wire auto-save, pass session-scoped agent
- `src/coding_agent/tui/app.py` — restore messages on mount, save after turns
- `src/coding_agent/slash_commands.py` — `/sessions`, `/resume`, `/new`
- `src/coding_agent/interactive_prompt.py` — plain-mode resume display
- `.gitignore` — ignore `.ai_history/sessions/` (user-local data)
- `tests/` — session store unit tests, resume smoke tests (plain mode)
- `README.md` — document session save/resume and slash commands
