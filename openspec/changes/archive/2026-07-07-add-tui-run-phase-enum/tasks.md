## 1. RunPhase enum

- [x] 1.1 Add `src/coding_agent/tui/run_phase.py` with `RunPhase(str, Enum)` — `IDLE`, `RUNNING`, `AWAITING_APPROVAL` (values `idle`, `running`, `awaiting_approval`)
- [x] 1.2 Add `coerce_run_phase(value: RunPhase | str) -> RunPhase` for slash/status callers

## 2. TUI integration

- [x] 2.1 Type `CodingAgentApp._run_phase` as `RunPhase`; initialize to `RunPhase.IDLE`
- [x] 2.2 Add `_set_run_phase(self, phase: RunPhase)` that assigns phase and updates footer when mounted
- [x] 2.3 Replace all string assignments in `tui/app.py` with `RunPhase` members via `_set_run_phase` (or direct assign where footer not needed yet)
- [x] 2.4 Use `self._run_phase.value` in `_footer_text` and when passing to `handle_slash_command`

## 3. Slash commands

- [x] 3.1 Update `format_status` and `handle_slash_command` to accept `RunPhase | str` and display `coerce_run_phase(...).value`

## 4. Tests

- [x] 4.1 Add `tests/test_run_phase.py` — enum values, `coerce_run_phase` accepts strings and rejects invalid values
- [x] 4.2 Extend `tests/test_tui_app.py` — approval flow sets `AWAITING_APPROVAL`, task completion returns to `IDLE`
- [x] 4.3 Update `tests/test_slash_commands.py` if signatures change
- [x] 4.4 Run full `pytest` suite and fix regressions

## 5. OpenSpec sync

- [x] 5.1 Archive change and sync main specs after implementation (`/opsx-archive`)
