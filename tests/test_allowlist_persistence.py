from pathlib import Path

from coding_agent.operation_allowlist import OperationAllowlist
from coding_agent.session import session_from_record, session_to_record
from coding_agent.config import Config
from coding_agent.session_store import SessionRecord, save_session, load_session, utc_now_iso


def _record(session_id: str, working_dir: Path) -> SessionRecord:
    now = utc_now_iso()
    return SessionRecord(
        id=session_id,
        title="test",
        created_at=now,
        updated_at=now,
        working_dir=str(working_dir.resolve()),
        current_model="gpt-4o-mini",
    )


def _config(working_dir: Path) -> Config:
    return Config(
        api_key="test-key",
        model="gpt-4o-mini",
        base_url="https://example.com/v1",
        max_steps=20,
        working_dir=working_dir,
    )


class TestAllowlistPersistence:
    def test_session_round_trip_preserves_allowlist(self, tmp_workdir):
        session = session_from_record(_record("abcd1234", tmp_workdir))
        session.operation_allowlist.approve(
            "write_file",
            '{"path": "hello.py", "content": "print(1)"}',
        )
        session.operation_allowlist.approve("run_shell", '{"command": "pytest"}')

        record = session_to_record(session, _config(tmp_workdir))
        save_session(record)

        loaded = session_from_record(load_session(tmp_workdir, "abcd1234"))
        assert loaded.operation_allowlist.is_allowed(
            "write_file",
            '{"path": "hello.py", "content": "other"}',
        )
        assert loaded.operation_allowlist.is_allowed(
            "run_shell",
            '{"command": "pytest"}',
        )

    def test_reset_for_new_clears_allowlist(self, tmp_workdir):
        session = session_from_record(_record("abcd1234", tmp_workdir))
        session.operation_allowlist.approve(
            "write_file",
            '{"path": "hello.py", "content": "x"}',
        )
        session.reset_for_new(_config(tmp_workdir))
        assert not session.operation_allowlist.is_allowed(
            "write_file",
            '{"path": "hello.py", "content": "x"}',
        )
