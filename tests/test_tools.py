import pytest

from coding_agent.config import Config, ConfigError
from coding_agent.tools.factory import create_default_registry
from coding_agent.tools.file_tools import create_file_tools
from coding_agent.tools.registry import ToolRegistry
from coding_agent.tools.shell_tools import create_shell_tools


class TestConfig:
    def test_missing_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ConfigError, match="API key is required"):
            Config.from_sources()

    def test_api_key_from_env(self, monkeypatch, tmp_workdir):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        config = Config.from_sources(cwd=str(tmp_workdir))
        assert config.api_key == "test-key"
        assert config.model == "gpt-4o-mini"

    def test_default_working_dir_is_cwd(self, monkeypatch, tmp_workdir):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.chdir(tmp_workdir)
        config = Config.from_sources()
        assert config.working_dir == tmp_workdir.resolve()
        assert config.working_dir.is_dir()


def _get_tool(registry: ToolRegistry, name: str):
    return registry._tools[name].func


class TestFileTools:
    def test_read_file(self, tmp_workdir):
        (tmp_workdir / "hello.txt").write_text("hello world", encoding="utf-8")
        registry = create_file_tools(tmp_workdir)
        read_file = _get_tool(registry, "read_file")
        assert read_file(path="hello.txt") == "hello world"

    def test_read_file_not_found(self, tmp_workdir):
        registry = create_file_tools(tmp_workdir)
        read_file = _get_tool(registry, "read_file")
        result = read_file(path="missing.txt")
        assert "not found" in result

    def test_read_file_truncation(self, tmp_workdir):
        lines = "\n".join(f"line {i}" for i in range(600))
        (tmp_workdir / "big.txt").write_text(lines, encoding="utf-8")
        registry = create_file_tools(tmp_workdir, line_limit=500)
        read_file = _get_tool(registry, "read_file")
        result = read_file(path="big.txt")
        assert "truncated" in result
        assert "line 0" in result
        assert "line 599" not in result

    def test_write_file(self, tmp_workdir):
        registry = create_file_tools(tmp_workdir)
        write_file = _get_tool(registry, "write_file")
        result = write_file(path="out.txt", content="data")
        assert "Successfully wrote" in result
        assert (tmp_workdir / "out.txt").read_text(encoding="utf-8") == "data"

    def test_write_file_nested(self, tmp_workdir):
        registry = create_file_tools(tmp_workdir)
        write_file = _get_tool(registry, "write_file")
        write_file(path="sub/out.txt", content="nested")
        assert (tmp_workdir / "sub" / "out.txt").read_text(encoding="utf-8") == "nested"

    def test_list_dir(self, tmp_workdir):
        (tmp_workdir / "a.txt").write_text("a", encoding="utf-8")
        (tmp_workdir / "subdir").mkdir()
        registry = create_file_tools(tmp_workdir)
        list_dir = _get_tool(registry, "list_dir")
        result = list_dir(path=".")
        assert "a.txt" in result
        assert "subdir/" in result

    def test_glob_files(self, tmp_workdir):
        (tmp_workdir / "a.py").write_text("x", encoding="utf-8")
        (tmp_workdir / "b.txt").write_text("y", encoding="utf-8")
        registry = create_file_tools(tmp_workdir)
        glob_files = _get_tool(registry, "glob_files")
        result = glob_files(pattern="*.py", path=".")
        assert "a.py" in result
        assert "b.txt" not in result

    def test_glob_files_no_matches(self, tmp_workdir):
        registry = create_file_tools(tmp_workdir)
        glob_files = _get_tool(registry, "glob_files")
        assert glob_files(pattern="*.rs", path=".") == "(no matches)"

    def test_search_code(self, tmp_workdir):
        (tmp_workdir / "main.py").write_text("def main():\n    pass\n", encoding="utf-8")
        registry = create_file_tools(tmp_workdir)
        search_code = _get_tool(registry, "search_code")
        result = search_code(pattern="def main", path=".", fixed_string=True)
        assert "main.py:1:" in result

    def test_edit_file(self, tmp_workdir):
        (tmp_workdir / "foo.py").write_text("hello world\n", encoding="utf-8")
        registry = create_file_tools(tmp_workdir)
        edit_file = _get_tool(registry, "edit_file")
        result = edit_file(path="foo.py", old_string="world", new_string="there")
        assert "Successfully edited" in result
        assert (tmp_workdir / "foo.py").read_text(encoding="utf-8") == "hello there\n"

    def test_edit_file_not_found(self, tmp_workdir):
        (tmp_workdir / "foo.py").write_text("hello\n", encoding="utf-8")
        registry = create_file_tools(tmp_workdir)
        edit_file = _get_tool(registry, "edit_file")
        result = edit_file(path="foo.py", old_string="missing", new_string="x")
        assert "not found" in result

    def test_edit_file_ambiguous(self, tmp_workdir):
        (tmp_workdir / "foo.py").write_text("x\nx\n", encoding="utf-8")
        registry = create_file_tools(tmp_workdir)
        edit_file = _get_tool(registry, "edit_file")
        result = edit_file(path="foo.py", old_string="x", new_string="y")
        assert "ambiguous" in result.lower() or "appears 2 times" in result

    def test_path_traversal_rejected(self, tmp_workdir):
        registry = create_file_tools(tmp_workdir)
        read_file = _get_tool(registry, "read_file")
        result = read_file(path="../../etc/passwd")
        assert "outside the working directory" in result

    def test_sensitive_file_read_blocked(self, tmp_workdir):
        (tmp_workdir / ".env").write_text("SECRET=1", encoding="utf-8")
        registry = create_file_tools(tmp_workdir)
        read_file = _get_tool(registry, "read_file")
        result = read_file(path=".env")
        assert "security policy" in result

    def test_sensitive_file_write_blocked(self, tmp_workdir):
        registry = create_file_tools(tmp_workdir)
        write_file = _get_tool(registry, "write_file")
        result = write_file(path=".env", content="SECRET=1")
        assert "security policy" in result

    def test_read_file_redacts_secrets(self, tmp_workdir):
        (tmp_workdir / "config.txt").write_text(
            "OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz", encoding="utf-8"
        )
        registry = create_file_tools(tmp_workdir)
        read_file = _get_tool(registry, "read_file")
        result = read_file(path="config.txt")
        assert "sk-abcdefghijklmnopqrstuvwxyz" not in result
        assert "[REDACTED]" in result


class TestShellTools:
    def test_run_shell_success(self, tmp_workdir):
        registry = create_shell_tools(tmp_workdir)
        run_shell = _get_tool(registry, "run_shell")
        result = run_shell(command="echo hello")
        assert "exit_code: 0" in result
        assert "hello" in result

    def test_run_shell_blocked(self, tmp_workdir):
        registry = create_shell_tools(tmp_workdir)
        run_shell = _get_tool(registry, "run_shell")
        result = run_shell(command="rm -rf /")
        assert "blocked by security policy" in result

    def test_run_shell_failure(self, tmp_workdir):
        registry = create_shell_tools(tmp_workdir)
        run_shell = _get_tool(registry, "run_shell")
        result = run_shell(command='python -c "import sys; sys.exit(1)"')
        assert "exit_code: 1" in result

    def test_run_shell_timeout(self, tmp_workdir):
        registry = create_shell_tools(tmp_workdir, timeout=1)
        run_shell = _get_tool(registry, "run_shell")
        result = run_shell(command='python -c "import time; time.sleep(5)"')
        assert "timed out" in result


class TestToolRegistry:
    def test_dispatch_unknown_tool(self):
        registry = ToolRegistry()
        result = registry.dispatch("missing", "{}")
        assert "not found" in result

    def test_get_schemas(self, tmp_workdir):
        registry = create_file_tools(tmp_workdir)
        schemas = registry.get_schemas()
        names = {s["function"]["name"] for s in schemas}
        assert names == {
            "read_file",
            "write_file",
            "list_dir",
            "glob_files",
            "search_code",
            "edit_file",
        }

    def test_default_registry_includes_new_tools(self, tmp_workdir):
        registry = create_default_registry(tmp_workdir)
        names = {s["function"]["name"] for s in registry.get_schemas()}
        assert {"glob_files", "search_code", "edit_file", "run_shell"}.issubset(names)
