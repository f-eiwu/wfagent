## 1. Operation Allowlist Core

- [x] 1.1 Create `src/coding_agent/operation_allowlist.py` with risk tier classification (`read_file`, `list_dir` auto; `write_file`, `run_shell` confirm)
- [x] 1.2 Implement allowlist key normalization (write: per path; shell: per command string)
- [x] 1.3 Implement `OperationAllowlist` on `SessionState` with `is_allowed`, `approve`, and clear on `/new` / new session
- [x] 1.4 Refactor `confirmation.py` to check allowlist, prompt, and record approvals (remove `auto_approve` parameter)

## 2. Agent and Tools

- [x] 2.1 Update `Agent._execute_tool` to use allowlist policy before dispatch
- [x] 2.2 Always register `run_shell` in `create_default_registry()` (remove `allow_shell` parameter)
- [x] 2.3 Update system prompt to reflect shell is available subject to user approval (remove allow_shell conditional)
- [x] 2.4 Require confirmation for all `write_file` calls (not only overwrites); remove `is_destructive` overwrite-only logic or fold into allowlist

## 3. Config and CLI Cleanup

- [x] 3.1 Remove `allow_shell` and `auto_approve` from `Config` and `from_sources`
- [x] 3.2 Remove `--allow-shell` and `--yes` from all CLI entry points (`main`, `resume`, `_load_config`)
- [x] 3.3 Remove `_print_security_warnings` and related startup messages
- [x] 3.4 Update confirmation error messages (remove references to `--yes`)

## 4. Interactive and TUI

- [x] 4.1 Pass session allowlist into `Agent` from plain interactive loop and TUI
- [x] 4.2 Ensure approval prompts work when agent runs in TUI worker thread (stderr prompt acceptable for v1)
- [x] 4.3 Clear allowlist on `/new` slash command

## 5. Tests and Documentation

- [x] 5.1 Add `tests/test_operation_allowlist.py` for tier classification, keys, and session remember/clear
- [x] 5.2 Update `tests/test_confirmation.py` for allowlist flow (remove auto_approve tests)
- [x] 5.3 Update `tests/test_cli.py` — remove `--allow-shell` / `--yes` tests; add non-TTY reject test for writes
- [x] 5.4 Update `tests/test_agent.py`, `tests/test_tools.py`, and other affected tests
- [x] 5.5 Update `README.md` security section and configuration table (remove flags, document allowlist model)
- [x] 5.6 Run full test suite (`pytest`) and verify all tests pass
