from rich.highlighter import Highlighter
from rich.text import Text
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Input, Static

from coding_agent.input_history import InputHistory, InputHistoryNavigator
from coding_agent.slash_highlight import stylize_slash_command


class SlashCommandHighlighter(Highlighter):
    """Highlight recognized slash commands in cyan while typing."""

    def highlight(self, text: Text) -> None:
        stylize_slash_command(text)


class HistoryInput(Input):
    """Single-line input with up/down history navigation."""

    BINDINGS = [
        *Input.BINDINGS,
        Binding("up", "history_previous", "Previous input", show=False),
        Binding("down", "history_next", "Next input", show=False),
    ]

    def __init__(
        self,
        input_history: InputHistory,
        *,
        highlighter: Highlighter | None = None,
        **kwargs,
    ) -> None:
        super().__init__(highlighter=highlighter, **kwargs)
        self._input_history = input_history
        self._navigator = InputHistoryNavigator(input_history)

    def push_history(self, text: str) -> None:
        self._input_history.push(text)
        self._navigator.reset()

    def action_history_previous(self) -> None:
        previous = self._navigator.previous(self.value)
        if previous is None:
            return
        self.value = previous
        self.cursor_position = len(self.value)

    def action_history_next(self) -> None:
        next_value = self._navigator.next()
        if next_value is None:
            return
        self.value = next_value
        self.cursor_position = len(self.value)


class FollowUpInput(Horizontal):
    """Bottom input row with arrow prefix and slash highlighting."""

    DEFAULT_CSS = """
    FollowUpInput {
        dock: bottom;
        margin-bottom: 1;
        height: 1;
        background: #1a1a1a;
        padding: 0 1;
    }

    FollowUpInput:focus-within {
        background: #252525;
    }

    FollowUpInput > .input-prefix {
        width: auto;
        color: #ffffff;
        padding: 0;
    }

    FollowUpInput > #follow-up-input {
        width: 1fr;
        border: none;
        background: transparent;
        padding: 0;
    }
    """

    def __init__(self, input_history: InputHistory, **kwargs) -> None:
        super().__init__(**kwargs)
        self._input_history = input_history

    def compose(self):
        yield Static("→ ", classes="input-prefix")
        yield HistoryInput(
            placeholder="Add a follow-up",
            id="follow-up-input",
            input_history=self._input_history,
            highlighter=SlashCommandHighlighter(),
        )
