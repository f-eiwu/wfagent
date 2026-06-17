from unittest.mock import patch

import pytest

from coding_agent.confirmation import require_approval
from coding_agent.operation_allowlist import OperationAllowlist, requires_confirmation


class TestRequiresConfirmation:
    def test_run_shell_requires_confirmation(self):
        assert requires_confirmation("run_shell") is True

    def test_write_file_requires_confirmation(self):
        assert requires_confirmation("write_file") is True

    def test_read_file_does_not_require_confirmation(self):
        assert requires_confirmation("read_file") is False


class TestRequireApproval:
    def test_allowlisted_operation_skips_prompt(self):
        allowlist = OperationAllowlist()
        allowlist.approve("run_shell", '{"command": "echo hi"}')
        approved, message = require_approval(
            "run_shell",
            '{"command": "echo hi"}',
            allowlist,
        )
        assert approved is True
        assert message == ""

    def test_custom_prompt_fn(self):
        allowlist = OperationAllowlist()
        approved, message = require_approval(
            "run_shell",
            '{"command": "pytest"}',
            allowlist,
            prompt_fn=lambda summary: summary.startswith("run_shell") and True,
        )
        assert approved is True
        assert allowlist.is_allowed("run_shell", '{"command": "pytest"}') is True

    def test_auto_approve_skips_prompt(self):
        allowlist = OperationAllowlist()
        approved, message = require_approval(
            "run_shell",
            '{"command": "echo hi"}',
            allowlist,
            auto_approve=True,
        )
        assert approved is True
        assert message == ""
        assert not allowlist.is_allowed("run_shell", '{"command": "echo hi"}')

    @patch("coding_agent.confirmation.sys.stdin.isatty", return_value=False)
    def test_non_tty_rejects_unlisted_operation(self, _isatty):
        allowlist = OperationAllowlist()
        approved, message = require_approval(
            "run_shell",
            '{"command": "echo hi"}',
            allowlist,
        )
        assert approved is False
        assert "confirmation required" in message

    @patch("coding_agent.confirmation.input", return_value="y")
    @patch("coding_agent.confirmation.sys.stdin.isatty", return_value=True)
    def test_user_approves_and_records_allowlist(self, _isatty, _input):
        allowlist = OperationAllowlist()
        args = '{"command": "pytest"}'
        approved, message = require_approval("run_shell", args, allowlist)
        assert approved is True
        assert allowlist.is_allowed("run_shell", args) is True

    @patch("coding_agent.confirmation.input", return_value="n")
    @patch("coding_agent.confirmation.sys.stdin.isatty", return_value=True)
    def test_user_rejects(self, _isatty, _input):
        allowlist = OperationAllowlist()
        approved, message = require_approval(
            "run_shell",
            '{"command": "echo hi"}',
            allowlist,
        )
        assert approved is False
        assert "rejected" in message
