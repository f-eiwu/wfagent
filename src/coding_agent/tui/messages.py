from dataclasses import dataclass
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class Message:
    role: MessageRole
    text: str


def format_step_progress(step: int, action: str) -> str:
    return f"→ [step {step}] {action}"


def message_css_class(role: MessageRole) -> str:
    return {
        MessageRole.USER: "user-message",
        MessageRole.ASSISTANT: "assistant-message",
        MessageRole.SYSTEM: "system-message",
    }[role]
