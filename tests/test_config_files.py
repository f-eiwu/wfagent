import pytest

from coding_agent.config import Config, ConfigError
from coding_agent.config_files import load_config_file, project_config_path


class TestLayeredConfig:
    def test_project_overrides_user(self, monkeypatch, tmp_workdir):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        user_dir = tmp_workdir / "user_cfg"
        user_dir.mkdir()
        user_file = user_dir / "config.toml"
        user_file.write_text('model = "user-model"\nmax_steps = 10\n', encoding="utf-8")
        (tmp_workdir / ".coding-agent.toml").write_text(
            'model = "project-model"\nmax_steps = 30\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(
            "coding_agent.config_files.user_config_path",
            lambda: user_file,
        )
        config = Config.from_sources(cwd=str(tmp_workdir))
        assert config.model == "project-model"
        assert config.max_steps == 30

    def test_cli_overrides_project_file(self, monkeypatch, tmp_workdir):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        (tmp_workdir / ".coding-agent.toml").write_text(
            'model = "project-model"\n',
            encoding="utf-8",
        )
        config = Config.from_sources(cwd=str(tmp_workdir), model="cli-model")
        assert config.model == "cli-model"

    def test_env_overrides_project_file(self, monkeypatch, tmp_workdir):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_MODEL", "env-model")
        (tmp_workdir / ".coding-agent.toml").write_text(
            'model = "project-model"\n',
            encoding="utf-8",
        )
        config = Config.from_sources(cwd=str(tmp_workdir))
        assert config.model == "env-model"

    def test_api_key_in_config_file_rejected(self, tmp_workdir):
        path = project_config_path(tmp_workdir)
        path.write_text('api_key = "secret"\n', encoding="utf-8")
        with pytest.raises(ConfigError, match="must not contain 'api_key'"):
            load_config_file(path)

    def test_request_timeout_from_project_file(self, monkeypatch, tmp_workdir):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        (tmp_workdir / ".coding-agent.toml").write_text(
            "request_timeout = 90\n",
            encoding="utf-8",
        )
        config = Config.from_sources(cwd=str(tmp_workdir))
        assert config.request_timeout == 90

    def test_log_level_from_project_file(self, monkeypatch, tmp_workdir):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        (tmp_workdir / ".coding-agent.toml").write_text(
            'log_level = "DEBUG"\n',
            encoding="utf-8",
        )
        config = Config.from_sources(cwd=str(tmp_workdir))
        assert config.log_level == "DEBUG"

    def test_env_overrides_log_level(self, monkeypatch, tmp_workdir):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("CODING_AGENT_LOG_LEVEL", "WARNING")
        (tmp_workdir / ".coding-agent.toml").write_text(
            'log_level = "DEBUG"\n',
            encoding="utf-8",
        )
        config = Config.from_sources(cwd=str(tmp_workdir))
        assert config.log_level == "WARNING"

    def test_cli_overrides_log_level(self, monkeypatch, tmp_workdir):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        (tmp_workdir / ".coding-agent.toml").write_text(
            'log_level = "WARNING"\n',
            encoding="utf-8",
        )
        config = Config.from_sources(cwd=str(tmp_workdir), log_level="ERROR")
        assert config.log_level == "ERROR"

    def test_invalid_log_level_rejected(self, tmp_workdir):
        path = project_config_path(tmp_workdir)
        path.write_text('log_level = "verbose"\n', encoding="utf-8")
        with pytest.raises(ConfigError, match="Invalid log level"):
            load_config_file(path)
