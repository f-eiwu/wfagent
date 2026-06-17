from textual.widgets import Static

from coding_agent.tui.messages import Message, message_css_class


class MessageWidget(Static):
    """A single conversation line with role-specific styling."""

    def __init__(self, message: Message) -> None:
        super().__init__(
            message.text,
            classes=message_css_class(message.role),
            markup=True,
        )


def create_message_widget(message: Message) -> Static:
    return MessageWidget(message)
