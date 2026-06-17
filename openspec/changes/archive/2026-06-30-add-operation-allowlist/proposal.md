## Why

Today the agent uses coarse global flags: `--allow-shell` gates whether shell exists at all, and `--yes` disables all confirmation prompts. That forces users to choose between “no shell” and “fully trusted automation,” which is unsafe for interactive use and awkward for one-shot scripts. A clearer model is to classify tools by risk, auto-run safe reads, and require explicit approval for file edits and shell commands—matching how modern coding agent treats risky operations.

## What Changes

- Introduce an **operation allowlist** with risk tiers: reads auto-execute; writes and shell require user confirmation first
- **Session-scoped allowlist**: once the user approves a specific write or shell operation, it may run again in the same session without re-prompting (same tool + normalized arguments)
- Register `run_shell` whenever the agent runs (subject to existing blocklist); remove the `--allow-shell` opt-in gate
- Require confirmation for **all** `write_file` calls (not only overwrites)
- Remove `--yes` / `auto_approve` global bypass
- **BREAKING**: Remove CLI flags `--allow-shell` and `--yes`; scripts must run interactively or pre-approve via session semantics
- Update confirmation UX in plain mode and TUI (prompt or in-conversation approval for risky ops)
- Remove startup security warnings tied to removed flags

## Capabilities

### New Capabilities

- `operation-allowlist`: Risk classification, per-operation confirmation, and session allowlist for approved writes and shell commands

### Modified Capabilities

- `confirmation-gate`: Replace auto-approve with allowlist-based approval; extend to all writes
- `shell-policy`: Shell always registered; confirmation + blocklist replace opt-in registration
- `cli`: Remove `--allow-shell` and `--yes`; update help and configuration docs
- `agent-core`: Route tool execution through allowlist policy before dispatch
- `coding-tools`: Clarify which tools are auto vs confirm-tier (behavior unchanged at tool layer)

## Impact

- `src/coding_agent/confirmation.py` — allowlist types, confirm + remember logic
- New `src/coding_agent/operation_allowlist.py` (or similar)
- `src/coding_agent/agent.py` — policy hook before `_execute_tool`
- `src/coding_agent/config.py` — remove `allow_shell`, `auto_approve`
- `src/coding_agent/cli.py` — remove flags and warnings
- `src/coding_agent/tools/factory.py` — always register shell tools
- `src/coding_agent/tui/app.py` — surface approval prompts in TUI when needed
- `tests/` — update confirmation, CLI, agent, tools tests
- `README.md` — document new security model
- **Breaking** for automation using `--allow-shell` or `--yes`
