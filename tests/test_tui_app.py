import asyncio
from unittest.mock import patch

import pytest
from textual.widgets import Input, Static

from coding_agent.config import Config
from coding_agent.session import SessionState
from coding_agent.tui import should_use_tui


async def _submit_line(app, pilot, text: str) -> None:
    inp = app.query_one("#follow-up-input", Input)
    inp.value = text
    await inp.action_submit()
    await pilot.pause(delay=0.3)


def _message_texts(app) -> list[str]:
    return [message.text for message in app._messages]


@pytest.fixture
def sample_config(tmp_workdir):
    return Config(
        api_key="test-key",
        model="gpt-4o-mini",
        base_url="https://example.com/v1",
        max_steps=5,
        working_dir=tmp_workdir.resolve(),
    )


@pytest.fixture
def sample_session():
    return SessionState(session_id="test1234", current_model="gpt-4o-mini")


class TestShouldUseTui:
    def test_plain_flag_disables_tui(self, monkeypatch):
        monkeypatch.setenv("CODING_AGENT_PLAIN_PROMPT", "")
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        assert should_use_tui(plain=True) is False

    def test_plain_prompt_env_disables_tui(self, monkeypatch):
        monkeypatch.setenv("CODING_AGENT_PLAIN_PROMPT", "1")
        assert should_use_tui(plain=False) is False

    def test_pytest_env_disables_tui(self, monkeypatch):
        monkeypatch.delenv("CODING_AGENT_PLAIN_PROMPT", raising=False)
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "test")
        assert should_use_tui(plain=False) is False


class TestCodingAgentApp:
    def test_exit_quits_app(self, sample_config, sample_session):
        from coding_agent.tui.app import CodingAgentApp

        async def run() -> None:
            app = CodingAgentApp(sample_config, sample_session)
            async with app.run_test() as pilot:
                await _submit_line(app, pilot, "exit")

        asyncio.run(run())

    def test_slash_help_shows_in_conversation(self, sample_config, sample_session):
        from coding_agent.tui.app import CodingAgentApp
        from coding_agent.tui.messages import MessageRole

        async def run() -> None:
            app = CodingAgentApp(sample_config, sample_session)
            async with app.run_test() as pilot:
                await _submit_line(app, pilot, "/help")
                assert app._messages[0].role is MessageRole.USER
                assert app._messages[0].text == "/help"
                assert any(
                    "Interactive commands:" in text for text in _message_texts(app)
                )

        asyncio.run(run())

    @patch("coding_agent.tui.app.Agent")
    def test_task_appends_user_and_assistant(
        self,
        mock_agent_cls,
        sample_config,
        sample_session,
    ):
        from coding_agent.tui.app import CodingAgentApp

        mock_agent_cls.return_value.run.return_value = "Done."

        async def run() -> None:
            app = CodingAgentApp(sample_config, sample_session)
            async with app.run_test() as pilot:
                await _submit_line(app, pilot, "hi")
                texts = _message_texts(app)
                assert "hi" in texts
                assert "Done." in texts

        asyncio.run(run())

    @patch("coding_agent.tui.app.Agent")
    def test_write_approval_prompt_in_conversation(
        self,
        mock_agent_cls,
        sample_config,
        sample_session,
    ):
        from coding_agent.tui.app import CodingAgentApp
        from coding_agent.tui.messages import MessageRole
        from coding_agent.tui.run_phase import RunPhase

        def fake_run(task: str, on_step=None, **kwargs):
            if on_step is not None:
                on_step("[step 1] write_file")
            approval_prompt = mock_agent_cls.call_args.kwargs["approval_prompt"]
            assert approval_prompt("write_file path=hello.py") is True
            return "Wrote hello.py"

        mock_agent_cls.return_value.run.side_effect = fake_run

        async def run() -> None:
            app = CodingAgentApp(sample_config, sample_session)
            async with app.run_test() as pilot:
                await _submit_line(app, pilot, "write hello.py")
                await pilot.pause(delay=0.1)
                assert app._run_phase is RunPhase.AWAITING_APPROVAL
                assert any(
                    "Approve write_file path=hello.py? [y/N]" in text
                    for text in _message_texts(app)
                )
                await _submit_line(app, pilot, "y")
                await pilot.pause(delay=0.2)
                assert app._run_phase is RunPhase.IDLE
                assert "Wrote hello.py" in _message_texts(app)
                assert any(
                    message.role is MessageRole.USER and message.text == "y"
                    for message in app._messages
                )

        asyncio.run(run())

    @patch("coding_agent.tui.app.Agent")
    def test_auto_approve_skips_approval_prompt(
        self,
        mock_agent_cls,
        sample_config,
        sample_session,
    ):
        from coding_agent.tui.app import CodingAgentApp

        sample_config.auto_approve = True
        mock_agent_cls.return_value.run.return_value = "Done."

        async def run() -> None:
            app = CodingAgentApp(sample_config, sample_session)
            async with app.run_test() as pilot:
                await _submit_line(app, pilot, "write hello.py")
                assert mock_agent_cls.call_args.kwargs.get("approval_prompt") is None

        asyncio.run(run())

    @patch("coding_agent.slash_commands.fetch_models")
    def test_model_switch_updates_footer(
        self,
        mock_fetch,
        sample_config,
        sample_session,
    ):
        from coding_agent.tui.app import CodingAgentApp

        mock_fetch.return_value = ["gpt-4o-mini", "gpt-4o"]

        async def run() -> None:
            app = CodingAgentApp(sample_config, sample_session)
            async with app.run_test() as pilot:
                await _submit_line(app, pilot, "/model gpt-4o")
                assert app._session.current_model == "gpt-4o"
                footer = app.query_one("#status-footer", Static)
                assert "gpt-4o" in str(footer.render())

        asyncio.run(run())

    @patch("coding_agent.tui.app.Agent")
    def test_input_history_with_up_arrow(
        self,
        mock_agent_cls,
        sample_config,
        sample_session,
    ):
        from coding_agent.tui.app import CodingAgentApp
        from coding_agent.tui.slash_input import HistoryInput

        mock_agent_cls.return_value.run.return_value = "Done."

        async def run() -> None:
            app = CodingAgentApp(sample_config, sample_session)
            async with app.run_test() as pilot:
                await _submit_line(app, pilot, "first task")
                await _submit_line(app, pilot, "second task")
                inp = app.query_one("#follow-up-input", HistoryInput)
                inp.value = ""
                await pilot.press("up")
                assert inp.value == "second task"
                await pilot.press("up")
                assert inp.value == "first task"
                await pilot.press("down")
                assert inp.value == "second task"
                await pilot.press("down")
                assert inp.value == ""

        asyncio.run(run())

    def test_status_shows_in_conversation(self, sample_config, sample_session):
        from coding_agent.tui.app import CodingAgentApp

        async def run() -> None:
            app = CodingAgentApp(sample_config, sample_session)
            async with app.run_test() as pilot:
                await _submit_line(app, pilot, "/status")
                assert any("Phase:" in text for text in _message_texts(app))
                assert any("Session:" in text for text in _message_texts(app))

        asyncio.run(run())

    @patch("coding_agent.tui.app.Agent")
    def test_task_sets_running_then_idle_phase(
        self,
        mock_agent_cls,
        sample_config,
        sample_session,
    ):
        from coding_agent.tui.app import CodingAgentApp
        from coding_agent.tui.run_phase import RunPhase

        mock_agent_cls.return_value.run.return_value = "Done."

        async def run() -> None:
            app = CodingAgentApp(sample_config, sample_session)
            async with app.run_test() as pilot:
                assert app._run_phase is RunPhase.IDLE
                await _submit_line(app, pilot, "hi")
                assert app._run_phase is RunPhase.IDLE

        asyncio.run(run())

    @patch("coding_agent.tui.app.Agent")
    def test_tool_events_in_conversation(
        self,
        mock_agent_cls,
        sample_config,
        sample_session,
    ):
        from coding_agent.tui.app import CodingAgentApp

        def fake_run(task: str, on_step=None, on_tool_call=None, on_tool_result=None, **kwargs):
            if on_tool_call is not None:
                on_tool_call("read_file", "read_file path=foo.py")
            if on_tool_result is not None:
                on_tool_result("read_file", "hello")
            return "Done."

        mock_agent_cls.return_value.run.side_effect = fake_run

        async def run() -> None:
            app = CodingAgentApp(sample_config, sample_session)
            async with app.run_test() as pilot:
                await _submit_line(app, pilot, "read foo")
                await pilot.pause(delay=0.3)
                texts = _message_texts(app)
                assert any("Tool call: read_file" in text for text in texts)
                assert any("Tool result: read_file" in text for text in texts)

        asyncio.run(run())
