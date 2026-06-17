## 1. Security Module

- [x] 1.1 Create `src/coding_agent/security/` package with `path_policy.py`, `shell_policy.py`, `redaction.py`
- [x] 1.2 Implement symlink-safe path resolution and sensitive-file glob denylist in `path_policy.py`
- [x] 1.3 Implement regex command blocklist and `is_command_allowed()` in `shell_policy.py`
- [x] 1.4 Implement secret redaction patterns in `redaction.py`
- [x] 1.5 Write `tests/test_security.py` covering path policy, shell blocklist, and redaction

## 2. Tool Hardening

- [x] 2.1 Update `file_tools.py` to use symlink-safe paths and sensitive-file checks
- [x] 2.2 Apply redaction to `read_file` output before returning
- [x] 2.3 Update `shell_tools.py` to check blocklist and prefer `shell=False` with `shlex.split` when safe
- [x] 2.4 Update `factory.py` to only include shell tools when `allow_shell` is true
- [x] 2.5 Update `tests/test_tools.py` for sensitive-file blocking and symlink rejection

## 3. Configuration and CLI

- [x] 3.1 Add `allow_shell` and `auto_approve` fields to `Config` in `config.py`
- [x] 3.2 Add `--allow-shell` and `--yes` flags to `cli.py`
- [x] 3.3 Print security warnings to stderr when `--allow-shell` or `--yes` is used
- [x] 3.4 Update `tests/test_cli.py` for new flags and help text

## 4. Confirmation Gate

- [x] 4.1 Implement `confirmation.py` with `is_destructive(tool_name, args)` and `confirm_action()`
- [x] 4.2 Integrate confirmation gate into `agent.py` before `registry.dispatch()`
- [x] 4.3 Handle non-TTY stdin: reject destructive calls without `--yes`
- [x] 4.4 Write `tests/test_confirmation.py` for prompt, reject, and auto-approve flows

## 5. Documentation and Verification

- [x] 5.1 Update README.md security section with new flags, defaults, and threat model
- [x] 5.2 Run full test suite (`pytest`) and verify all tests pass
- [x] 5.3 Manual smoke test: confirm shell is blocked by default and confirmation prompt appears on file overwrite
