## Context

The coding agent (`src/coding_agent/`) currently has minimal security: path traversal checks via `resolve()`, but uses `shell=True` with no restrictions, no symlink hardening, no sensitive-file filtering, and no user confirmation before destructive actions. The default working directory is `deliverables/`, but tools can still overwrite files and run shell commands freely when enabled.

## Goals / Non-Goals

**Goals:**
- Reduce blast radius of LLM-initiated tool calls
- Make dangerous operations opt-in (`--allow-shell`) or require explicit approval (`--yes` to skip prompts)
- Harden file path handling against symlinks and sensitive paths
- Redact secrets from content returned to the LLM

**Non-Goals:**
- Full sandboxing (Docker, seccomp, firejail)
- Network egress filtering
- Cryptographic signing of tool calls
- Audit log persistence to disk (stderr warnings only in v1)

## Decisions

### 1. Shell tool disabled by default

**Decision:** `run_shell` is not registered unless `config.allow_shell=True` (CLI: `--allow-shell`).

**Rationale:** Shell is the highest-risk tool. Most coding tasks (read/write/list) work without it. Users who need shell must explicitly opt in.

### 2. Regex-based command blocklist

**Decision:** Central `security/shell_policy.py` with a list of compiled regex patterns blocking commands like `rm -rf`, `del /f`, `format`, `curl|bash`, `wget|sh`, fork bombs, etc.

**Rationale:** Simple, testable, no external deps. Not foolproof against obfuscation, but catches common destructive patterns.

**Alternative considered:** Allowlist-only — too restrictive for a general coding agent.

### 3. Symlink-safe path resolution

**Decision:** Replace naive `resolve()` with `Path.resolve()` then verify `os.path.samefile` or check that resolved path's parent chain stays under `working_dir.resolve()`. Reject if any symlink in chain escapes (use `is_symlink()` on resolved components).

**Rationale:** `Path.resolve()` follows symlinks; we additionally reject paths whose resolved target is outside cwd.

### 4. Sensitive file denylist

**Decision:** `security/path_policy.py` with glob patterns: `.env`, `.env.*`, `*.pem`, `*.key`, `*credentials*`, `*secret*`, `.git/config`, etc. Applied to `read_file` and `write_file`.

**Rationale:** Prevents accidental secret exfiltration or overwrite. `list_dir` still shows names but not contents.

### 5. Confirmation gate in agent loop

**Decision:** Before executing a tool classified as destructive (`run_shell`, `write_file` on existing file), prompt on stderr: `Approve [tool_name]? [y/N]`. Skip if `--yes` or non-interactive stdin.

**Rationale:** Gives user a chance to veto bad LLM decisions without blocking all automation.

**Classification:**
- `run_shell` — always destructive
- `write_file` — destructive only when target file already exists
- `read_file`, `list_dir` — not destructive

### 6. Output redaction

**Decision:** `security/redaction.py` applies regex to tool output before returning to LLM: `sk-...`, `Bearer ...`, long hex tokens, `password=...` patterns.

**Rationale:** Defense in depth if a secret file is read despite denylist.

### 7. Module layout

```
src/coding_agent/security/
├── __init__.py
├── path_policy.py      # symlink check, sensitive patterns
├── shell_policy.py     # blocklist, is_allowed()
└── redaction.py        # scrub secrets from strings
```

`agent.py` calls confirmation gate before `registry.dispatch()`. `config.py` adds `allow_shell: bool` and `auto_approve: bool`.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Blocklist bypass via obfuscation | Document limitation; confirmation gate as second layer |
| `--yes` disables safety | Warn on startup when `--yes` and `--allow-shell` combined |
| Symlink check platform differences | Test on Windows and POSIX; use `resolve(strict=False)` |
| Breaking existing workflows | Document `--allow-shell`; shell was implicit before |
| False positives on blocklist | Keep patterns conservative; return clear error message |

## Migration Plan

1. Ship with shell disabled by default
2. Update README: add `--allow-shell` to examples that need shell
3. Existing scripts: add `--allow-shell` flag

## Open Questions

- Should `list_dir` hide sensitive filenames? **Decision: no** — hiding names adds complexity; deny read/write only.
- Non-interactive mode without `--yes` on destructive ops? **Decision: reject** with error "confirmation required".
