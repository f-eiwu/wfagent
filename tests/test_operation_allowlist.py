from coding_agent.operation_allowlist import (
    OperationAllowlist,
    allowlist_key,
    requires_confirmation,
)


class TestRequiresConfirmation:
    def test_read_tools_are_auto(self):
        assert requires_confirmation("read_file") is False
        assert requires_confirmation("list_dir") is False

    def test_write_and_shell_require_confirmation(self):
        assert requires_confirmation("write_file") is True
        assert requires_confirmation("run_shell") is True


class TestAllowlistKey:
    def test_write_file_key_uses_path_only(self):
        key = allowlist_key(
            "write_file",
            '{"path": "src/foo.py", "content": "hello"}',
        )
        assert key == ("write_file", "src/foo.py")

    def test_run_shell_key_uses_command(self):
        key = allowlist_key("run_shell", '{"command": "pytest"}')
        assert key == ("run_shell", "pytest")

    def test_auto_tool_has_no_key(self):
        assert allowlist_key("read_file", '{"path": "x.txt"}') is None


class TestOperationAllowlist:
    def test_approve_and_remember_write_path(self):
        allowlist = OperationAllowlist()
        args = '{"path": "foo.py", "content": "a"}'
        assert allowlist.is_allowed("write_file", args) is False
        allowlist.approve("write_file", args)
        assert allowlist.is_allowed("write_file", args) is True
        other_content = '{"path": "foo.py", "content": "b"}'
        assert allowlist.is_allowed("write_file", other_content) is True

    def test_different_paths_require_separate_approval(self):
        allowlist = OperationAllowlist()
        allowlist.approve("write_file", '{"path": "a.py", "content": "x"}')
        assert allowlist.is_allowed("write_file", '{"path": "b.py", "content": "x"}') is False

    def test_clear_resets_entries(self):
        allowlist = OperationAllowlist()
        allowlist.approve("run_shell", '{"command": "pytest"}')
        allowlist.clear()
        assert allowlist.is_allowed("run_shell", '{"command": "pytest"}') is False

    def test_entries_round_trip(self):
        allowlist = OperationAllowlist()
        allowlist.approve("write_file", '{"path": "foo.py", "content": "x"}')
        allowlist.approve("run_shell", '{"command": "pytest"}')
        restored = OperationAllowlist.from_entries(allowlist.entries())
        assert restored.is_allowed("write_file", '{"path": "foo.py", "content": "y"}') is True
        assert restored.is_allowed("run_shell", '{"command": "pytest"}') is True
        assert restored.is_allowed("write_file", '{"path": "bar.py", "content": "x"}') is False
