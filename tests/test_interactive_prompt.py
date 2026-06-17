from prompt_toolkit.document import Document

from coding_agent.interactive_prompt import (
    _SlashCommandLexer,
    _line_fragments,
)


class TestSlashCommandLexer:
    def test_highlights_help_with_argument(self):
        lexer = _SlashCommandLexer()
        fragments = lexer.lex_document(Document("/help model"))(0)
        assert fragments == [("class:slash-command", "/help"), ("", " model")]

    def test_highlights_help_command(self):
        lexer = _SlashCommandLexer()
        fragments = lexer.lex_document(Document("/help"))(0)
        assert fragments == [("class:slash-command", "/help")]

    def test_highlights_complete_slash_command(self):
        lexer = _SlashCommandLexer()
        fragments = lexer.lex_document(Document("/model"))(0)
        assert fragments == [("class:slash-command", "/model")]

    def test_highlights_command_with_argument(self):
        lexer = _SlashCommandLexer()
        fragments = lexer.lex_document(Document("/model gpt-4o-mini"))(0)
        assert fragments == [
            ("class:slash-command", "/model"),
            ("", " gpt-4o-mini"),
        ]

    def test_no_highlight_for_partial_command(self):
        assert _line_fragments("/mod") == [("", "/mod")]

    def test_no_highlight_for_unknown_command(self):
        assert _line_fragments("/foo") == [("", "/foo")]

    def test_no_highlight_for_plain_task(self):
        assert _line_fragments("write a game") == [("", "write a game")]

    def test_empty_line(self):
        assert _line_fragments("") == []
