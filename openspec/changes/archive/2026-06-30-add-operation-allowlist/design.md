## Context

Security today uses two CLI flags:

- `--allow-shell` — registers `run_shell` in the tool registry
- `--yes` — sets `auto_approve` and skips all confirmation prompts

`confirmation.py` treats `run_shell` and `write_file` on existing files as “destructive.” `read_file` and `list_dir` run without prompts. Non-TTY stdin rejects destructive ops unless `--yes`.

The user wants a modern agent-style model: reads are safe and automatic; edits and shell need explicit approval, without global bypass flags.

## Goals / Non-Goals

**Goals:**

- Classify tools into auto (read/list) vs confirm (write/shell)
- Prompt before first execution of each distinct confirm-tier operation
- Remember approved operations in a **session allowlist** so identical repeats do not re-prompt
- Always expose `run_shell` (blocklist still applies before execution)
- Confirm all `write_file` calls, including new files
- Remove `--allow-shell` and `--yes` from CLI and `Config`
- Work in plain interactive mode and TUI (approval visible in conversation when using TUI)

**Non-Goals:**

- Persistent allowlist across sessions or on disk
- Per-project config file for permanent allow rules
- GUI modal dialogs beyond terminal prompt / TUI system message
- Changing path denylist, redaction, or shell blocklist patterns (keep existing)
- Allowlisting by wildcard patterns (“allow all writes to `src/`”) in v1

## Decisions

### 1. Risk tiers

| Tier | Tools | Behavior |
|------|-------|----------|
| Auto | `read_file`, `list_dir` | Execute immediately |
| Confirm | `write_file`, `run_shell` | Require approval unless on session allowlist |

### 2. Allowlist key

**Decision:** Key = `(tool_name, normalized_arguments_json)` where arguments are parsed JSON with stable key ordering for hashing/equality.

**Rationale:** Same write or shell command approved once per session should not spam prompts. Different paths/commands are distinct entries.

**Example keys:**
- `("write_file", '{"path":"foo.py","content":"..."}')` — content included so editing same file with new content re-prompts
- Alternative considered: key only on `path` for writes — rejected because content changes matter

Actually for write_file, if we include full content in key, every edit re-prompts even to same file. User might want "approve write to foo.py" for session. 

**Revised decision for writes:** Key = `write_file` + normalized `path` only (approve path for session).
**For shell:** Key = `run_shell` + normalized `command` string (exact command for session).

### 3. Session allowlist ownership

**Decision:** `OperationAllowlist` lives on `SessionState`, cleared on `/new` and new session. Passed into `Agent` or confirmation gate.

**Rationale:** Aligns with session-scoped model selection; no cross-session trust bleed.

### 4. Approval flow

```
LLM requests tool
  → classify tier
  → if auto: dispatch
  → if confirm:
       if key in allowlist: dispatch
       else: prompt user
         if approved: add to allowlist, dispatch
         else: return rejection to LLM
```

**Plain mode:** stderr prompt `Approve write_file path=foo.py? [y/N]` (show summary, not full content).

**TUI mode:** append system notice + use threaded prompt or `input()` via `call_from_thread` — v1 may use same stderr prompt from worker thread or inline system message “approve in terminal”; prefer reusing confirmation module with optional `stream` callback for TUI text.

**Non-TTY one-shot `--task`:** reject confirm-tier ops with clear error (“confirmation required; run interactively”). No `--yes` escape hatch.

### 5. Remove allow_shell registration gate

**Decision:** `create_default_registry()` always includes `run_shell`. System prompt always mentions shell availability (subject to user approval).

**Rationale:** User explicitly asked to remove `--allow-shell`. Shell is available but never silent.

### 6. Remove auto_approve

**Decision:** Delete `auto_approve` from `Config` and all call sites. Tests use mocked approval or pre-seeded allowlist.

### 7. Module layout

```
src/coding_agent/
  operation_allowlist.py   # OperationAllowlist, risk tier, allowlist key helpers
  confirmation.py          # prompt UI, delegates allowlist check
```

`Agent._execute_tool` calls `require_approval(tool, args, allowlist)` before dispatch.

### 8. CLI cleanup

Remove from `cli.py`, `resume_command`, `_load_config`:
- `--allow-shell`, `--yes`
- `_print_security_warnings` for those flags

Update README configuration table and security section.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Breaking scripts using `--yes` | Document migration; one-shot non-TTY cannot run writes/shell |
| TUI approval UX awkward from worker thread | v1: stderr prompt; future: native TUI modal |
| Path-only write allowlist approves any content to path | Document; user can `/new` to reset allowlist |
| LLM spams small distinct shell commands | Each unique command prompts once per session only |

## Migration Plan

**Breaking change.**

1. Remove flags from CLI and docs
2. Always register shell in factory
3. Replace `auto_approve` checks with allowlist
4. Update tests: remove `--allow-shell`/`--yes` cases; add allowlist tests
5. README: explain auto reads vs confirm writes/shell

## Open Questions

- TUI: inline y/n in input area vs stderr prompt (recommend stderr for v1 simplicity)
- Whether `write_file` allowlist should be per-path or per full arguments (design: per-path)
