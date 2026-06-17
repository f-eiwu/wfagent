from __future__ import annotations

from enum import Enum


class RunPhase(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"


def coerce_run_phase(value: RunPhase | str) -> RunPhase:
    if isinstance(value, RunPhase):
        return value
    return RunPhase(value)
