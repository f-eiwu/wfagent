from datetime import UTC, datetime
from pathlib import Path

import pytest

from coding_agent.session_store import (
    AmbiguousSessionIdError,
    SessionNotFoundError,
    SessionRecord,
    delete_session,
    latest_session,
    list_sessions,
    load_session,
    resolve_session_choice,
    save_session,
    sessions_dir,
    utc_now_iso,
)


def _record(
    session_id: str,
    working_dir: Path,
    *,
    title: str = "test",
    updated_at: str | None = None,
) -> SessionRecord:
    now = updated_at or utc_now_iso()
    return SessionRecord(
        id=session_id,
        title=title,
        created_at=now,
        updated_at=now,
        working_dir=str(working_dir.resolve()),
        current_model="gpt-4o-mini",
        display_messages=[{"role": "user", "text": "hello"}],
        agent_messages=[{"role": "system", "content": "sys"}],
        input_history=["hello"],
    )


class TestSessionStore:
    def test_sessions_dir_under_working_dir(self, tmp_workdir):
        assert sessions_dir(tmp_workdir) == tmp_workdir / ".ai_history" / "sessions"

    def test_save_and_load_round_trip(self, tmp_workdir):
        record = _record("abcd1234", tmp_workdir, title="round trip")
        record.operation_allowlist = [
            ["write_file", "hello.py"],
            ["run_shell", "pytest"],
        ]
        save_session(record)
        loaded = load_session(tmp_workdir, "abcd1234")
        assert loaded.id == "abcd1234"
        assert loaded.title == "round trip"
        assert loaded.display_messages[0]["text"] == "hello"
        assert loaded.operation_allowlist == [
            ["write_file", "hello.py"],
            ["run_shell", "pytest"],
        ]

    def test_load_missing_allowlist_defaults_empty(self, tmp_workdir):
        record = _record("abcd1234", tmp_workdir)
        save_session(record)
        loaded = load_session(tmp_workdir, "abcd1234")
        assert loaded.operation_allowlist == []

    def test_load_by_prefix(self, tmp_workdir):
        save_session(_record("abcd1234", tmp_workdir))
        loaded = load_session(tmp_workdir, "abcd")
        assert loaded.id == "abcd1234"

    def test_ambiguous_prefix_raises(self, tmp_workdir):
        save_session(_record("abcd1234", tmp_workdir))
        save_session(_record("abcd5678", tmp_workdir, title="other"))
        with pytest.raises(AmbiguousSessionIdError):
            load_session(tmp_workdir, "abcd")

    def test_missing_session_raises(self, tmp_workdir):
        with pytest.raises(SessionNotFoundError):
            load_session(tmp_workdir, "missing")

    def test_list_sessions_filters_by_working_dir(self, tmp_workdir):
        other = tmp_workdir / "other"
        other.mkdir()
        older = _record(
            "11111111",
            tmp_workdir,
            title="older",
            updated_at="2026-01-01T00:00:00Z",
        )
        newer = _record(
            "22222222",
            tmp_workdir,
            title="newer",
            updated_at="2026-06-01T00:00:00Z",
        )
        foreign = _record("33333333", other, title="foreign")
        save_session(older)
        save_session(newer)
        save_session(foreign)

        sessions = list_sessions(tmp_workdir)
        assert [session.id for session in sessions] == ["22222222", "11111111"]

    def test_latest_session(self, tmp_workdir):
        save_session(
            _record("11111111", tmp_workdir, updated_at="2026-01-01T00:00:00Z")
        )
        save_session(
            _record("22222222", tmp_workdir, updated_at="2026-06-01T00:00:00Z")
        )
        latest = latest_session(tmp_workdir)
        assert latest is not None
        assert latest.id == "22222222"

    def test_resolve_session_choice_by_number(self, tmp_workdir):
        first = _record("abcd1234", tmp_workdir, title="first")
        second = _record("deadbeef", tmp_workdir, title="second")
        sessions = [first, second]
        assert resolve_session_choice(tmp_workdir, sessions, "2").id == "deadbeef"

    def test_resolve_session_choice_invalid_number(self, tmp_workdir):
        sessions = [_record("abcd1234", tmp_workdir)]
        with pytest.raises(SessionNotFoundError):
            resolve_session_choice(tmp_workdir, sessions, "9")

    def test_delete_session(self, tmp_workdir):
        record = _record("abcd1234", tmp_workdir)
        save_session(record)
        deleted = delete_session(tmp_workdir, "abcd1234")
        assert deleted.id == "abcd1234"
        with pytest.raises(SessionNotFoundError):
            load_session(tmp_workdir, "abcd1234")
