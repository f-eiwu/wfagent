from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from coding_agent.cli import app
from coding_agent.session_store import SessionRecord, save_session, sessions_dir, utc_now_iso


def _record(
    session_id: str,
    working_dir,
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

runner = CliRunner()

pytestmark = pytest.mark.usefixtures("plain_interactive_prompt")


@pytest.fixture
def plain_interactive_prompt(monkeypatch):
    monkeypatch.setenv("CODING_AGENT_PLAIN_PROMPT", "1")


class TestSessionResume:
    def test_interactive_creates_session_file(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        result = runner.invoke(app, input="exit\n")
        assert result.exit_code == 0
        session_files = list(sessions_dir(tmp_workdir).glob("*.json"))
        assert len(session_files) == 1

    @patch("coding_agent.cli.Agent")
    def test_cross_turn_agent_reuses_messages(self, mock_agent_cls, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        agent = MagicMock()
        agent.run.side_effect = ["first", "second"]
        agent.messages = [{"role": "system", "content": "sys"}]
        mock_agent_cls.return_value = agent

        result = runner.invoke(app, input="task one\ntask two\nexit\n")
        assert result.exit_code == 0
        assert mock_agent_cls.call_count == 1
        assert agent.run.call_count == 2

    @patch("coding_agent.cli.Agent")
    def test_resume_flag_restores_session(self, mock_agent_cls, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        record = _record("abcd1234", tmp_workdir, title="saved")
        save_session(record)

        agent = MagicMock()
        agent.run.return_value = "ok"
        agent.messages = record.agent_messages
        mock_agent_cls.return_value = agent

        result = runner.invoke(app, ["--resume", "abcd1234"], input="exit\n")
        assert result.exit_code == 0
        assert "abcd1234" in result.stderr

    @patch("coding_agent.cli.Agent")
    def test_continue_uses_latest_session(self, mock_agent_cls, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        save_session(
            _record("11111111", tmp_workdir, updated_at="2026-01-01T00:00:00Z")
        )
        save_session(
            _record("22222222", tmp_workdir, updated_at="2026-06-01T00:00:00Z")
        )

        mock_agent_cls.return_value = MagicMock(messages=[])

        result = runner.invoke(app, ["--continue"], input="exit\n")
        assert result.exit_code == 0
        assert "22222222" in result.stderr


class TestSessionSlashCommands:
    def test_sessions_lists_saved(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        save_session(_record("abcd1234", tmp_workdir, title="my chat"))
        result = runner.invoke(app, input="/sessions\nexit\n")
        assert result.exit_code == 0
        assert "abcd1234" in result.stderr
        assert "my chat" in result.stderr

    def test_new_starts_fresh_session(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        result = runner.invoke(app, input="/new\nexit\n")
        assert result.exit_code == 0
        assert "Started new session" in result.stderr

    def test_resume_slash_loads_session(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        save_session(_record("abcd1234", tmp_workdir, title="saved"))
        result = runner.invoke(app, input="/resume abcd1234\nexit\n")
        assert result.exit_code == 0
        assert "Resumed session abcd1234" in result.stderr


class TestSessionListAndPick:
    def test_ls_lists_numbered_sessions(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        save_session(_record("abcd1234", tmp_workdir, title="first"))
        save_session(_record("deadbeef", tmp_workdir, title="second"))
        result = runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "1  abcd1234" in result.stdout or "1  deadbeef" in result.stdout
        assert "Sessions:" in result.stdout

    def test_ls_empty(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        result = runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "No saved sessions" in result.stdout

    @patch("coding_agent.cli.Agent")
    def test_resume_picks_by_number(self, mock_agent_cls, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        save_session(_record("abcd1234", tmp_workdir, title="first"))
        save_session(_record("deadbeef", tmp_workdir, title="second"))
        mock_agent_cls.return_value = MagicMock(messages=[])

        result = runner.invoke(app, ["resume", "--plain"], input="2\nexit\n")
        assert result.exit_code == 0
        assert "deadbeef" in result.stderr

    @patch("coding_agent.cli.Agent")
    def test_resume_starts_new_on_n(self, mock_agent_cls, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        save_session(_record("abcd1234", tmp_workdir, title="first"))
        mock_agent_cls.return_value = MagicMock(messages=[])

        result = runner.invoke(app, ["resume", "--plain"], input="n\nexit\n")
        assert result.exit_code == 0
        assert "Interactive mode" in result.stderr
        assert "abcd1234 ·" not in result.stderr

    def test_rm_command_deletes_session(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        save_session(_record("abcd1234", tmp_workdir, title="to delete"))
        result = runner.invoke(app, ["rm", "abcd1234"])
        assert result.exit_code == 0
        assert "Removed session abcd1234" in result.stdout
        assert not list(sessions_dir(tmp_workdir).glob("*.json"))

    def test_rm_slash_deletes_other_session(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        save_session(_record("abcd1234", tmp_workdir, title="other"))
        result = runner.invoke(app, input="/rm abcd1234\nexit\n")
        assert result.exit_code == 0
        assert "Removed session abcd1234" in result.stderr
        assert not list(sessions_dir(tmp_workdir).glob("abcd1234.json"))

    @patch("coding_agent.cli.Agent")
    def test_rm_slash_deletes_current_session(self, mock_agent_cls, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_agent_cls.return_value = MagicMock(messages=[])
        result = runner.invoke(app, input="/sessions\nexit\n")
        assert result.exit_code == 0
        session_id = None
        for line in result.stderr.splitlines():
            if line.strip().startswith("1  "):
                session_id = line.split()[1]
                break
        assert session_id is not None

        result = runner.invoke(app, input=f"/rm {session_id}\nexit\n")
        assert result.exit_code == 0
        assert f"Removed session {session_id}" in result.stderr
        assert "Started new session" not in result.stderr
        assert f"{session_id} ·" not in result.stderr
