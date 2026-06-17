## Context

`interactive-tui` spec already requires phases `idle`, `running`, and `awaiting_approval`. `MessageRole` in `tui/messages.py` already uses `str, Enum`. `_run_phase` is set in five places in `app.py` and passed as `str` to `format_status`.

## Goals / Non-Goals

**Goals:**
- Define `RunPhase(str, Enum)` with exactly the three spec values
- Type `_run_phase` as `RunPhase` on `CodingAgentApp`
- Use `.value` when formatting footer and `/status` text
- Optional `_set_phase(phase: RunPhase)` that updates footer when phase changes

**Non-Goals:**
- Agent-core state machine (agent loop stays callback-driven)
- New phases such as `error` (errors stay as conversation messages; phase returns to `idle`)
- Pause/cancel mid-run
- Persisting phase to session files

## Decisions

### 1. Module location

**Decision:** Add `src/coding_agent/tui/run_phase.py` with `RunPhase` enum.

**Rationale:** Keeps `messages.py` focused on display messages; run phase is TUI runtime state, not message content.

**Alternative:** Put in `messages.py` next to `MessageRole` → acceptable but mixes concerns.

### 2. String enum for JSON/display compatibility

**Decision:** `class RunPhase(str, Enum)` so `.value` and str comparison stay stable and `format_status` can accept `RunPhase | str` with normalization.

**Rationale:** Footer and `/status` already show lowercase strings; no migration needed.

### 3. Centralized setter

**Decision:** Add `_set_run_phase(self, phase: RunPhase) -> None` on `CodingAgentApp` that assigns `_run_phase` and calls `_update_footer()` when the footer is mounted.

**Rationale:** Reduces scattered `_run_phase = ...; _update_footer()` pairs; not a full state machine table yet.

### 4. Slash command typing

**Decision:** Change `format_status` and `handle_slash_command` `run_phase` parameter type to `RunPhase | str`, coercing via `RunPhase(phase)` or a small `coerce_run_phase()` helper.

**Rationale:** Plain-mode callers can still pass `"idle"`; TUI passes `RunPhase.IDLE`.

## Risks / Trade-offs

- **[Risk] Invalid string passed to slash status** → Mitigation: `coerce_run_phase` raises `ValueError` or defaults to `idle` only in tests; TUI always passes enum
- **[Risk] Over-engineering transitions** → Mitigation: no transition matrix; only enum + setter

## Migration Plan

1. Add `RunPhase` enum and tests
2. Update `CodingAgentApp` assignments
3. Update `slash_commands.py` signatures
4. Run full pytest

## Open Questions

- None
