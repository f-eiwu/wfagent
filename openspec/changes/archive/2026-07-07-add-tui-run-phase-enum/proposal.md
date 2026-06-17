## Why

`CodingAgentApp._run_phase` is stored as ad-hoc strings (`"idle"`, `"running"`, `"awaiting_approval"`) assigned in multiple methods (`tui/app.py`). This is error-prone, hard to refactor, and was flagged in the evaluate-agent rubric under「显式状态机」. The OpenSpec already defines the three allowed phase values; an Enum makes that contract explicit in code.

## What Changes

- Introduce a `RunPhase` enum (`str, Enum`) with values `idle`, `running`, and `awaiting_approval`
- Replace `_run_phase` string assignments in `CodingAgentApp` with enum members
- Add a small helper to set phase and refresh the footer in one place (optional centralized transitions)
- Update `format_status` / `handle_slash_command` to accept `RunPhase` (or stringify via `.value` for display)
- Add unit tests for enum values and TUI phase transitions
- No user-visible behavior change: footer and `/status` still show the same phase strings

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `interactive-tui`: Clarify that run phase is represented by a typed enum in code while preserving the three documented phase strings for display

## Impact

- **Code:** new `tui/run_phase.py` (or `tui/messages.py` extension), `tui/app.py`, `slash_commands.py`
- **APIs:** internal only; `/status` output unchanged
- **Dependencies:** none
- **Tests:** extend `test_tui_app.py` and/or new `test_run_phase.py`; update `test_slash_commands.py`
