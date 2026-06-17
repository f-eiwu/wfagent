from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from coding_agent.cli import app

runner = CliRunner()

pytestmark = pytest.mark.usefixtures("plain_interactive_prompt")


@pytest.fixture
def plain_interactive_prompt(monkeypatch):
    monkeypatch.setenv("CODING_AGENT_PLAIN_PROMPT", "1")


class TestCLI:
    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "coding-agent" in result.stdout.lower()
        assert "--cwd" in result.stdout
        assert "--api-key" in result.stdout
        assert "--model" in result.stdout
        assert "--base-url" in result.stdout
        assert "--max-steps" in result.stdout
        assert "--yes" in result.stdout
        assert "-y" in result.stdout
        assert "--plain" in result.stdout
        assert "--resume" in result.stdout
        assert "--continue" in result.stdout
        assert "--task" not in result.stdout

    def test_help_lists_subcommands(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ls" in result.stdout
        assert "resume" in result.stdout
        assert "rm" in result.stdout

    def test_missing_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        result = runner.invoke(app, input="exit\n")
        assert result.exit_code == 1
        assert "API key is required" in result.stderr

    @patch("coding_agent.cli._run_agent")
    def test_cwd_flag(self, mock_run, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_run.return_value = MagicMock()
        result = runner.invoke(
            app,
            ["--cwd", str(tmp_workdir)],
            input="list files\nexit\n",
        )
        assert result.exit_code == 0
        config = mock_run.call_args[0][0]
        assert config.working_dir == tmp_workdir.resolve()

    @patch("coding_agent.cli._run_agent")
    def test_model_override(self, mock_run, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_run.return_value = MagicMock()
        result = runner.invoke(
            app,
            ["--model", "gpt-4o"],
            input="test\nexit\n",
        )
        assert result.exit_code == 0
        config = mock_run.call_args[0][0]
        assert config.model == "gpt-4o"

    def test_yes_flag(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        result = runner.invoke(app, ["--yes"], input="exit\n")
        assert result.exit_code == 0
        assert "without confirmation" in result.stderr

    def test_y_short_flag(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        result = runner.invoke(app, ["-y"], input="exit\n")
        assert result.exit_code == 0
        assert "without confirmation" in result.stderr

    @patch("coding_agent.cli.pick_session")
    @patch("coding_agent.cli._start_interactive")
    def test_resume_yes_flag(self, mock_start, mock_pick, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_pick.return_value = object()
        result = runner.invoke(app, ["resume", "-y"])
        assert result.exit_code == 0
        config = mock_start.call_args[0][0]
        assert config.auto_approve is True
        assert "without confirmation" in result.stderr

    @patch("coding_agent.cli.pick_session")
    @patch("coding_agent.cli._start_interactive")
    def test_global_yes_before_resume_subcommand(self, mock_start, mock_pick, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_pick.return_value = object()
        result = runner.invoke(app, ["-y", "resume"])
        assert result.exit_code == 0
        config = mock_start.call_args[0][0]
        assert config.auto_approve is True

    def test_interactive_models_hint(self, monkeypatch, tmp_workdir):
        monkeypatch.chdir(tmp_workdir)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        result = runner.invoke(app, input="exit\n")
        assert result.exit_code == 0
        assert "/help" in result.stderr
        assert "gpt-4o-mini" in result.stderr
        assert str(tmp_workdir.resolve()) in result.stderr

    @patch("coding_agent.cli._run_agent")
    def test_interactive_help(self, mock_run, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        result = runner.invoke(app, input="/help\nexit\n")
        assert result.exit_code == 0
        mock_run.assert_not_called()
        assert "Interactive commands:" in result.stderr
        assert "/model" in result.stderr
        assert "/help" in result.stderr
        assert "exit" in result.stderr

    @patch("coding_agent.cli._run_agent")
    def test_interactive_help_specific_command(self, mock_run, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        result = runner.invoke(app, input="/help model\nexit\n")
        assert result.exit_code == 0
        mock_run.assert_not_called()
        assert "/model" in result.stderr
        assert "provider API" in result.stderr

    @patch("coding_agent.cli._run_agent")
    def test_interactive_help_unknown_topic(self, mock_run, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        result = runner.invoke(app, input="/help foo\nexit\n")
        assert result.exit_code == 0
        mock_run.assert_not_called()
        assert "unknown help topic" in result.stderr.lower()

    @patch("coding_agent.slash_commands.fetch_models")
    @patch("coding_agent.cli._run_agent")
    def test_interactive_models_list(self, mock_run, mock_fetch, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_fetch.return_value = ["gpt-4o-mini", "gpt-4o"]
        result = runner.invoke(app, input="/model\nexit\n")
        assert result.exit_code == 0
        mock_run.assert_not_called()
        assert "gpt-4o-mini" in result.stderr
        assert "\033[32m" in result.stderr or "gpt-4o-mini" in result.stderr

    @patch("coding_agent.slash_commands.fetch_models")
    @patch("coding_agent.cli._run_agent")
    def test_interactive_models_switch(self, mock_run, mock_fetch, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_fetch.return_value = ["gpt-4o-mini", "gpt-4o"]
        result = runner.invoke(app, input="/model gpt-4o\nexit\n")
        assert result.exit_code == 0
        mock_run.assert_not_called()
        assert "Switched to gpt-4o" in result.stderr

    @patch("coding_agent.slash_commands.fetch_models")
    @patch("coding_agent.cli._run_agent")
    def test_interactive_models_switch_used_on_task(self, mock_run, mock_fetch, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_fetch.return_value = ["gpt-4o-mini", "gpt-4o"]
        result = runner.invoke(
            app,
            input="/model gpt-4o\nhello\nexit\n",
        )
        assert result.exit_code == 0
        mock_run.assert_called_once()
        session = mock_run.call_args[0][1]
        assert session.current_model == "gpt-4o"

    @patch("coding_agent.slash_commands.fetch_models")
    @patch("coding_agent.cli._run_agent")
    def test_interactive_models_invalid_switch(self, mock_run, mock_fetch, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_fetch.return_value = ["gpt-4o-mini"]
        result = runner.invoke(app, input="/model bad-model\nexit\n")
        assert result.exit_code == 0
        mock_run.assert_not_called()
        assert "unknown model" in result.stderr.lower()

    @patch("coding_agent.cli._run_agent")
    def test_interactive_unknown_slash_command(self, mock_run, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        result = runner.invoke(app, input="/foo\nexit\n")
        assert result.exit_code == 0
        mock_run.assert_not_called()
        assert "Try /help." in result.stderr
