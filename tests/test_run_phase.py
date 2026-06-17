import pytest

from coding_agent.tui.run_phase import RunPhase, coerce_run_phase


class TestRunPhase:
    def test_enum_values(self):
        assert RunPhase.IDLE.value == "idle"
        assert RunPhase.RUNNING.value == "running"
        assert RunPhase.AWAITING_APPROVAL.value == "awaiting_approval"

    def test_coerce_accepts_enum(self):
        assert coerce_run_phase(RunPhase.RUNNING) is RunPhase.RUNNING

    def test_coerce_accepts_string(self):
        assert coerce_run_phase("idle") is RunPhase.IDLE

    def test_coerce_rejects_invalid_string(self):
        with pytest.raises(ValueError):
            coerce_run_phase("busy")
