from dataclasses import dataclass, field

from prompt_toolkit.history import History


@dataclass
class InputHistory:
    """Session-scoped submitted input lines, oldest first."""

    _entries: list[str] = field(default_factory=list)

    def push(self, text: str) -> None:
        line = text.strip()
        if not line or line.lower() == "exit":
            return
        if self._entries and self._entries[-1] == line:
            return
        self._entries.append(line)

    def entries(self) -> list[str]:
        return list(self._entries)


class PromptToolkitHistory(History):
    """prompt_toolkit history backed by InputHistory."""

    def __init__(self, store: InputHistory) -> None:
        super().__init__()
        self._store = store

    def load_history_strings(self):
        return self._store.entries()

    def store_string(self, string: str) -> None:
        self._store.push(string)


class InputHistoryNavigator:
    """Navigate submitted input with up/down arrows."""

    def __init__(self, history: InputHistory) -> None:
        self._history = history
        self._index = -1
        self._draft = ""

    def reset(self) -> None:
        self._index = -1
        self._draft = ""

    def previous(self, current: str) -> str | None:
        entries = self._history.entries()
        if not entries:
            return None
        if self._index == -1:
            self._draft = current
            self._index = len(entries) - 1
        elif self._index > 0:
            self._index -= 1
        else:
            return None
        return entries[self._index]

    def next(self) -> str | None:
        entries = self._history.entries()
        if not entries or self._index == -1:
            return None
        if self._index < len(entries) - 1:
            self._index += 1
            return entries[self._index]
        self._index = -1
        return self._draft
