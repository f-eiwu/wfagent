from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coding_agent.agent import Agent
from coding_agent.config import Config
from coding_agent.logging_config import setup_logging
from coding_agent.operation_allowlist import OperationAllowlist
from coding_agent.tools.file_tools import create_file_tools


def _make_config(tmp_path: Path, max_steps: int = 20) -> Config:
    return Config(
        api_key="test-key",
        model="gpt-4o-mini",
        base_url="https://api.openai.com/v1",
        max_steps=max_steps,
        working_dir=tmp_path,
    )


def _approved_allowlist(tool_name: str, arguments: str) -> OperationAllowlist:
    allowlist = OperationAllowlist()
    allowlist.approve(tool_name, arguments)
    return allowlist


class TestAgent:
    def test_one_shot_completion(self, tmp_workdir):
        config = _make_config(tmp_workdir)
        llm = MagicMock()
        llm.chat.return_value = {
            "role": "assistant",
            "content": "Task complete.",
            "tool_calls": None,
        }
        setup_logging("INFO")
        agent = Agent(config, llm=llm, tools=create_file_tools(tmp_workdir))
        result = agent.run("Say hello")
        assert result == "Task complete."
        assert llm.chat.call_count == 1

    def test_multi_step_tool_use(self, tmp_workdir, capsys):
        config = _make_config(tmp_workdir)
        write_args = '{"path": "hello.py", "content": "print(\\"hi\\")"}'
        llm = MagicMock()
        llm.chat.side_effect = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "write_file",
                            "arguments": write_args,
                        },
                    }
                ],
            },
            {
                "role": "assistant",
                "content": "Created hello.py",
                "tool_calls": None,
            },
        ]
        setup_logging("INFO")
        agent = Agent(
            config,
            llm=llm,
            tools=create_file_tools(tmp_workdir),
            allowlist=_approved_allowlist("write_file", write_args),
        )
        result = agent.run("Create hello.py")
        captured = capsys.readouterr()
        assert result == "Created hello.py"
        assert (tmp_workdir / "hello.py").read_text(encoding="utf-8") == 'print("hi")'
        assert llm.chat.call_count == 2
        assert "write_file" in captured.err

    def test_headless_run_logs_steps(self, tmp_workdir, capsys):
        setup_logging("INFO")
        config = _make_config(tmp_workdir)
        llm = MagicMock()
        llm.chat.return_value = {
            "role": "assistant",
            "content": "Done.",
            "tool_calls": None,
        }
        agent = Agent(config, llm=llm, tools=create_file_tools(tmp_workdir))
        agent.run("hello")
        captured = capsys.readouterr()
        assert "[step 1] thinking" in captured.err

    def test_callback_suppresses_step_logs(self, tmp_workdir, capsys):
        setup_logging("INFO")
        config = _make_config(tmp_workdir)
        llm = MagicMock()
        llm.chat.return_value = {
            "role": "assistant",
            "content": "Done.",
            "tool_calls": None,
        }
        agent = Agent(config, llm=llm, tools=create_file_tools(tmp_workdir))
        steps: list[str] = []

        def on_step(message: str) -> None:
            steps.append(message)

        agent.run("hello", on_step=on_step)
        captured = capsys.readouterr()
        assert steps
        assert "[step 1] thinking" not in captured.err

    @patch("coding_agent.confirmation.sys.stdin.isatty", return_value=False)
    def test_write_rejected_on_non_tty(self, _isatty, tmp_workdir):
        config = _make_config(tmp_workdir)
        write_args = '{"path": "hello.py", "content": "x"}'
        llm = MagicMock()
        llm.chat.side_effect = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "write_file",
                            "arguments": write_args,
                        },
                    }
                ],
            },
            {
                "role": "assistant",
                "content": "Could not write file.",
                "tool_calls": None,
            },
        ]
        agent = Agent(config, llm=llm, tools=create_file_tools(tmp_workdir))
        agent.run("Create hello.py")
        second_call_messages = llm.chat.call_args_list[1][0][0]
        tool_messages = [m for m in second_call_messages if m.get("role") == "tool"]
        assert len(tool_messages) == 1
        assert "confirmation required" in tool_messages[0]["content"]
        assert not (tmp_workdir / "hello.py").exists()

    @patch("coding_agent.confirmation.sys.stdin.isatty", return_value=False)
    def test_write_allowed_on_non_tty_with_auto_approve(self, _isatty, tmp_workdir):
        config = _make_config(tmp_workdir)
        config = Config(
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url,
            max_steps=config.max_steps,
            working_dir=config.working_dir,
            auto_approve=True,
        )
        write_args = '{"path": "hello.py", "content": "x"}'
        llm = MagicMock()
        llm.chat.side_effect = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "write_file",
                            "arguments": write_args,
                        },
                    }
                ],
            },
            {
                "role": "assistant",
                "content": "Created hello.py",
                "tool_calls": None,
            },
        ]
        agent = Agent(config, llm=llm, tools=create_file_tools(tmp_workdir))
        agent.run("Create hello.py")
        assert (tmp_workdir / "hello.py").read_text(encoding="utf-8") == "x"

    def test_step_limit_reached(self, tmp_workdir):
        config = _make_config(tmp_workdir, max_steps=2)
        llm = MagicMock()
        llm.chat.return_value = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "list_dir",
                        "arguments": "{}",
                    },
                }
            ],
        }
        agent = Agent(config, llm=llm, tools=create_file_tools(tmp_workdir))
        result = agent.run("Keep listing")
        assert "Step limit of 2 reached" in result
        assert llm.chat.call_count == 2

    def test_system_prompt_includes_working_dir(self, tmp_workdir):
        config = _make_config(tmp_workdir)
        llm = MagicMock()
        llm.chat.return_value = {
            "role": "assistant",
            "content": "done",
            "tool_calls": None,
        }
        agent = Agent(config, llm=llm, tools=create_file_tools(tmp_workdir))
        agent.run("test")
        messages = llm.chat.call_args[0][0]
        system_msg = messages[0]["content"]
        assert str(tmp_workdir) in system_msg
        assert "user approval" in system_msg

    @patch("coding_agent.confirmation.sys.stdin.isatty", return_value=True)
    @patch("coding_agent.confirmation.input", return_value="n")
    def test_rejection_in_tool_history(self, _input, _isatty, tmp_workdir):
        config = _make_config(tmp_workdir)
        write_args = '{"path": "hello.py", "content": "x"}'
        llm = MagicMock()
        llm.chat.side_effect = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "write_file",
                            "arguments": write_args,
                        },
                    }
                ],
            },
            {
                "role": "assistant",
                "content": "Could not write.",
                "tool_calls": None,
            },
        ]
        rejected: list[tuple[str, str]] = []

        def on_rejected(name: str, reason: str) -> None:
            rejected.append((name, reason))

        agent = Agent(config, llm=llm, tools=create_file_tools(tmp_workdir))
        agent.run("Create hello.py", on_tool_rejected=on_rejected)
        assert rejected
        assert "rejected" in rejected[0][1].lower()
        tool_messages = [
            m for m in llm.chat.call_args_list[1][0][0] if m.get("role") == "tool"
        ]
        assert "rejected" in tool_messages[0]["content"].lower()
