import io
import threading
from importlib.metadata import PackageNotFoundError, version

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Header, Input, Static

from coding_agent.agent import Agent
from coding_agent.config import Config
from coding_agent.llm import LLMError
from coding_agent.session import (
    SessionState,
    config_with_model,
    maybe_set_session_title,
    persist_session_state,
)
from coding_agent.slash_commands import SlashOutcome, handle_slash_command
from coding_agent.tui.messages import Message, MessageRole
from coding_agent.tui.run_phase import RunPhase
from coding_agent.tui.slash_input import FollowUpInput, HistoryInput
from coding_agent.tui.widgets import create_message_widget

_INPUT_PLACEHOLDER = "Add a follow-up"
_APPROVAL_PLACEHOLDER = "y or n to approve"


def _app_version() -> str:
    try:
        return version("coding-agent")
    except PackageNotFoundError:
        return "dev"


class CodingAgentApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "Coding Agent"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("ctrl+q", "quit", "Quit", show=False),
    ]

    def __init__(self, config: Config, session: SessionState) -> None:
        super().__init__()
        self._config = config
        self._session = session
        self._messages: list[Message] = list(session.display_messages)
        self._approval_event = threading.Event()
        self._approval_result = False
        self._awaiting_approval = False
        self._run_phase = RunPhase.IDLE
        self._streaming_assistant = False
        self._agent = self._make_agent()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static(self._subheader_text(), id="app-subheader")
        yield VerticalScroll(id="conversation")
        yield FollowUpInput(self._session.input_history)
        yield Static(self._footer_text(), id="status-footer")

    def on_mount(self) -> None:
        self.sub_title = f"v{_app_version()}"
        self._render_all_messages()
        self.query_one("#follow-up-input", HistoryInput).focus()

    def _make_agent(self) -> Agent:
        agent_config = config_with_model(self._config, self._session.current_model)
        messages = self._session.agent_messages or None
        approval_prompt = (
            None if agent_config.auto_approve else self._request_approval
        )
        return Agent(
            agent_config,
            messages=messages,
            allowlist=self._session.operation_allowlist,
            approval_prompt=approval_prompt,
        )

    def _request_approval(self, summary: str) -> bool:
        self._approval_event.clear()
        self._approval_result = False
        self.call_from_thread(self._show_approval_prompt, summary)
        self._approval_event.wait()
        return self._approval_result

    def _show_approval_prompt(self, summary: str) -> None:
        self._set_run_phase(RunPhase.AWAITING_APPROVAL)
        self._awaiting_approval = True
        self._append_system(f"Approve {summary}? [y/N]")
        history_input = self.query_one("#follow-up-input", HistoryInput)
        history_input.placeholder = _APPROVAL_PLACEHOLDER
        history_input.focus()

    def _finish_approval(self, approved: bool) -> None:
        self._approval_result = approved
        self._awaiting_approval = False
        self._set_run_phase(RunPhase.RUNNING)
        self._approval_event.set()
        history_input = self.query_one("#follow-up-input", HistoryInput)
        history_input.placeholder = _INPUT_PLACEHOLDER
        history_input.focus()

    def _set_run_phase(self, phase: RunPhase) -> None:
        self._run_phase = phase
        if self.is_running:
            self._update_footer()

    def _subheader_text(self) -> str:
        return "Use /help for commands (e.g. /help model, /status)."

    def _footer_text(self) -> str:
        auto = " · auto-approve" if self._config.auto_approve else ""
        return (
            f"{self._session.session_id} · "
            f"{self._session.current_model} · {self._config.working_dir} · "
            f"{self._run_phase.value}{auto}"
        )

    def _update_footer(self) -> None:
        self.query_one("#status-footer", Static).update(self._footer_text())

    def _render_all_messages(self) -> None:
        scroll = self.query_one("#conversation", VerticalScroll)
        for child in list(scroll.children):
            child.remove()
        for message in self._messages:
            scroll.mount(create_message_widget(message))
        scroll.scroll_end(animate=False)

    def _reload_from_session(self) -> None:
        self._messages = list(self._session.display_messages)
        self._agent = self._make_agent()
        self._render_all_messages()
        self._update_footer()

    def _append_message(self, message: Message) -> None:
        self._messages.append(message)
        scroll = self.query_one("#conversation", VerticalScroll)
        scroll.mount(create_message_widget(message))
        scroll.scroll_end(animate=False)

    def _append_user(self, text: str) -> None:
        self._append_message(Message(MessageRole.USER, text))

    def _append_assistant(self, text: str) -> None:
        self._append_message(Message(MessageRole.ASSISTANT, text))

    def _append_system(self, text: str) -> None:
        if text.strip():
            self._append_message(Message(MessageRole.SYSTEM, text.strip()))

    def _append_or_extend_assistant(self, text: str) -> None:
        if (
            self._streaming_assistant
            and self._messages
            and self._messages[-1].role is MessageRole.ASSISTANT
        ):
            last = self._messages[-1]
            updated = Message(MessageRole.ASSISTANT, last.text + text)
            self._messages[-1] = updated
            scroll = self.query_one("#conversation", VerticalScroll)
            children = list(scroll.children)
            if children:
                children[-1].update(updated.text)
            scroll.scroll_end(animate=False)
            return
        self._streaming_assistant = True
        self._append_assistant(text)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        history_input = self.query_one("#follow-up-input", HistoryInput)
        history_input.push_history(text)
        event.input.value = ""
        if not text:
            return
        if self._awaiting_approval:
            self._append_user(text)
            approved = text.lower() in ("y", "yes")
            if not approved:
                self._append_system("Rejected: user declined approval")
            self._finish_approval(approved)
            return
        if text.lower() == "exit":
            persist_session_state(self._session, self._config)
            self.exit()
            return
        if text.startswith("/"):
            self._append_user(text)
            self._handle_slash(text)
            return
        self._append_user(text)
        self.run_worker(lambda: self._run_task(text), thread=True)

    def _handle_slash(self, line: str) -> None:
        buffer = io.StringIO()
        outcome = handle_slash_command(
            line,
            self._session,
            self._config,
            stream=buffer,
            run_phase=self._run_phase,
        )
        output = buffer.getvalue().strip()
        if output:
            self._append_system(output)
        if outcome.reset_agent:
            command = line.strip().split(maxsplit=1)[0].lower()
            if command in {"/resume", "/new", "/clear", "/rm"}:
                self._reload_from_session()
                if output:
                    self._append_system(output)
            else:
                self._agent = self._make_agent()
                self._update_footer()
        else:
            self._update_footer()
        self._session.display_messages = list(self._messages)
        if outcome.handled:
            persist_session_state(self._session, self._config)

    def _run_task(self, task: str) -> None:
        self.call_from_thread(self._begin_task)

        def on_step(message: str) -> None:
            self.call_from_thread(self._append_system, message)

        def on_tool_call(_name: str, summary: str) -> None:
            self.call_from_thread(self._append_system, f"Tool call: {summary}")

        def on_tool_result(name: str, summary: str) -> None:
            self.call_from_thread(
                self._append_system,
                f"Tool result: {name} — {summary}",
            )

        def on_tool_rejected(_name: str, reason: str) -> None:
            self.call_from_thread(self._append_system, f"Rejected: {reason}")

        def on_stream_chunk(chunk: str) -> None:
            self.call_from_thread(self._append_or_extend_assistant, chunk)

        try:
            result = self._agent.run(
                task,
                on_step=on_step,
                on_tool_call=on_tool_call,
                on_tool_result=on_tool_result,
                on_tool_rejected=on_tool_rejected,
                on_stream_chunk=on_stream_chunk,
            )
        except LLMError as exc:
            self.call_from_thread(self._finish_task_error, str(exc))
            return

        self.call_from_thread(self._finalize_task, task, result)

    def _begin_task(self) -> None:
        self._set_run_phase(RunPhase.RUNNING)
        self._streaming_assistant = False

    def _finish_task_error(self, message: str) -> None:
        self._set_run_phase(RunPhase.IDLE)
        self._streaming_assistant = False
        self._append_system(f"Error: {message}")

    def _last_assistant_message(self) -> Message | None:
        for message in reversed(self._messages):
            if message.role is MessageRole.ASSISTANT:
                return message
        return None

    def _finalize_task(self, task: str, result: str) -> None:
        self._set_run_phase(RunPhase.IDLE)
        self._streaming_assistant = False
        last_assistant = self._last_assistant_message()
        if last_assistant is None:
            self._append_assistant(result)
        elif last_assistant.text != result:
            idx = self._messages.index(last_assistant)
            updated = Message(MessageRole.ASSISTANT, result)
            self._messages[idx] = updated
            scroll = self.query_one("#conversation", VerticalScroll)
            for child in scroll.children:
                if getattr(child, "text", None) == last_assistant.text:
                    child.update(result)
                    break
        self._session.agent_messages = list(self._agent.messages)
        self._session.display_messages = list(self._messages)
        maybe_set_session_title(self._session, task)
        persist_session_state(self._session, self._config)

    async def action_quit(self) -> None:
        persist_session_state(self._session, self._config)
        self.exit()
