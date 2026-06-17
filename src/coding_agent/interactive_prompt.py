import os
import sys

from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.history import History
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style

from coding_agent.slash_highlight import recognized_slash_command_end

_PROMPT_STYLE = Style.from_dict(
    {
        "slash-command": "ansicyan bold",
        "prompt": "",
    }
)


def _line_fragments(text: str) -> StyleAndTextTuples:
    if not text:
        return []

    command_end = recognized_slash_command_end(text)
    if command_end is None:
        return [("", text)]

    fragments: StyleAndTextTuples = [("class:slash-command", text[:command_end])]
    if command_end < len(text):
        fragments.append(("", text[command_end:]))
    return fragments


class _SlashCommandLexer(Lexer):
    def lex_document(self, document: Document):
        def get_line(lineno: int) -> StyleAndTextTuples:
            try:
                return _line_fragments(document.lines[lineno])
            except IndexError:
                return []

        return get_line


def _use_prompt_toolkit(*, plain: bool = False) -> bool:
    if plain:
        return False
    if os.environ.get("CODING_AGENT_PLAIN_PROMPT"):
        return False
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    return sys.stdin.isatty() and sys.stdout.isatty()


def read_task_input(
    *,
    plain: bool = False,
    history: History | None = None,
) -> str:
    if not _use_prompt_toolkit(plain=plain):
        return input("task> ").strip()

    return prompt(
        [("class:prompt", "task> ")],
        lexer=_SlashCommandLexer(),
        style=_PROMPT_STYLE,
        history=history,
    ).strip()
