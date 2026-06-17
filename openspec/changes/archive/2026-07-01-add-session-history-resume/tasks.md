## 1. Session Store

- [x] 1.1 Create `src/coding_agent/session_store.py` with `SessionRecord` dataclass matching design schema (v1)
- [x] 1.2 Implement `sessions_dir(working_dir) -> Path` resolving `.ai_history/sessions/`
- [x] 1.3 Implement `save_session(record)` writing atomic JSON (write temp + rename)
- [x] 1.4 Implement `load_session(working_dir, id) -> SessionRecord` with prefix matching and ambiguity error
- [x] 1.5 Implement `list_sessions(working_dir) -> list[SessionRecord]` filtered by cwd, sorted by `updated_at` desc
- [x] 1.6 Implement `latest_session(working_dir) -> SessionRecord | None`
- [x] 1.7 Add `.ai_history/sessions/` to `.gitignore`

## 2. Session State and Agent

- [x] 2.1 Extend `SessionState` with `session_id`, `title`, `display_messages`, `agent_messages`, timestamps
- [x] 2.2 Add `new_session(config) -> SessionState` and `session_from_record(record) -> SessionState` helpers
- [x] 2.3 Add optional `messages` parameter and `messages` property to `Agent`
- [x] 2.4 Add `sync_session_after_run(session, agent, display_updates)` helper to merge agent messages and display lines after a task

## 3. CLI Flags and Lifecycle

- [x] 3.1 Add `--resume <id>` and `--continue` flags to `cli.py` (mutually exclusive, incompatible with `--task`)
- [x] 3.2 On interactive start: load session from flags or create new session; call `save_session` for new sessions
- [x] 3.3 Reuse one `Agent` instance (or equivalent message list) across plain interactive loop turns
- [x] 3.4 Call `save_session` after each task and slash command that mutates session; save on graceful exit
- [x] 3.5 Show short session id in `_print_session_status` for plain mode

## 4. Slash Commands

- [x] 4.1 Implement `/sessions` listing in `slash_commands.py`
- [x] 4.2 Implement `/resume <id>` loading session and returning status text for UI refresh
- [x] 4.3 Implement `/new` creating fresh session id and clearing messages
- [x] 4.4 Set session title from first user task (max 80 chars)
- [x] 4.5 Update `/help` output to document session commands

## 5. TUI Integration

- [x] 5.1 Accept preloaded `display_messages` in `CodingAgentApp` and render on mount
- [x] 5.2 After each task, persist session via `save_session` from TUI worker completion
- [x] 5.3 Handle `/resume` and `/new` by clearing and repopulating conversation widgets
- [x] 5.4 Add session short id to footer alongside model and working directory
- [x] 5.5 Save session on TUI exit (`exit` keyword and quit bindings)

## 6. Tests and Documentation

- [x] 6.1 Add `tests/test_session_store.py` for save/load/list/prefix-match and cwd filtering
- [x] 6.2 Add `tests/test_session_resume.py` for plain-mode resume and cross-turn agent context
- [x] 6.3 Add tests for `/sessions`, `/resume`, `/new` slash commands
- [x] 6.4 Add test that `--task` does not create session files
- [x] 6.5 Update `README.md` with session save/resume usage (`--resume`, `--continue`, slash commands)
- [x] 6.6 Run full test suite (`pytest`) and verify all tests pass
