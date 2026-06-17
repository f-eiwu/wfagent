from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from coding_agent.config import Config
from coding_agent.input_history import InputHistory
from coding_agent.operation_allowlist import OperationAllowlist
from coding_agent.session_store import SessionRecord, new_session_id, save_session, utc_now_iso
from coding_agent.tui.messages import Message, MessageRole


@dataclass
class SessionState:
    session_id: str
    current_model: str
    title: str = ""
    created_at: str = ""
    updated_at: str = ""
    display_messages: list[Message] = field(default_factory=list)
    agent_messages: list[dict[str, Any]] = field(default_factory=list)
    input_history: InputHistory = field(default_factory=InputHistory)
    operation_allowlist: OperationAllowlist = field(default_factory=OperationAllowlist)
    _prompt_history: object = field(default=None, repr=False, compare=False)

    def get_prompt_history(self):
        from coding_agent.input_history import PromptToolkitHistory

        if self._prompt_history is None:
            self._prompt_history = PromptToolkitHistory(self.input_history)
        return self._prompt_history

    def load_from_record(self, record: SessionRecord) -> None:
        self.session_id = record.id
        self.title = record.title
        self.created_at = record.created_at
        self.updated_at = record.updated_at
        self.current_model = record.current_model
        self.display_messages = [
            Message(MessageRole(item["role"]), item["text"])
            for item in record.display_messages
        ]
        self.agent_messages = list(record.agent_messages)
        self.input_history = InputHistory()
        for line in record.input_history:
            self.input_history.push(line)
        self.operation_allowlist = OperationAllowlist.from_entries(record.operation_allowlist)
        self._prompt_history = None

    def reset_for_new(self, config: Config) -> None:
        now = utc_now_iso()
        self.session_id = new_session_id()
        self.title = ""
        self.created_at = now
        self.updated_at = now
        self.current_model = config.model
        self.display_messages = []
        self.agent_messages = []
        self.input_history = InputHistory()
        self.operation_allowlist.clear()
        self._prompt_history = None


def config_with_model(config: Config, model: str) -> Config:
    return replace(config, model=model)


def new_session(config: Config) -> SessionState:
    now = utc_now_iso()
    return SessionState(
        session_id=new_session_id(),
        current_model=config.model,
        title="",
        created_at=now,
        updated_at=now,
    )


def session_from_record(record: SessionRecord) -> SessionState:
    session = SessionState(
        session_id=record.id,
        current_model=record.current_model,
        title=record.title,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )
    session.load_from_record(record)
    return session


def session_to_record(session: SessionState, config: Config) -> SessionRecord:
    return SessionRecord(
        version=1,
        id=session.session_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        working_dir=str(config.working_dir.resolve()),
        current_model=session.current_model,
        display_messages=[
            {"role": message.role.value, "text": message.text}
            for message in session.display_messages
        ],
        agent_messages=list(session.agent_messages),
        input_history=session.input_history.entries(),
        operation_allowlist=session.operation_allowlist.entries(),
    )


def persist_session_state(session: SessionState, config: Config) -> None:
    session.updated_at = utc_now_iso()
    save_session(session_to_record(session, config))


def maybe_set_session_title(session: SessionState, task: str) -> None:
    if session.title:
        return
    line = task.strip()
    if not line or line.startswith("/"):
        return
    session.title = line[:80]


def sync_session_after_run(
    session: SessionState,
    agent_messages: list[dict[str, Any]],
    *,
    user_text: str,
    assistant_text: str,
    system_lines: list[str] | None = None,
) -> None:
    session.agent_messages = list(agent_messages)
    session.display_messages.append(Message(MessageRole.USER, user_text))
    for line in system_lines or []:
        if line.strip():
            session.display_messages.append(Message(MessageRole.SYSTEM, line.strip()))
    session.display_messages.append(Message(MessageRole.ASSISTANT, assistant_text))
    maybe_set_session_title(session, user_text)
