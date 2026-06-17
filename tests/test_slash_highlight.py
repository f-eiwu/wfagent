from rich.text import Text

from coding_agent.slash_highlight import recognized_slash_command_end, stylize_slash_command


class TestSlashHighlight:
    def test_recognized_help_command(self):
        assert recognized_slash_command_end("/help") == 5

    def test_recognized_help_with_argument(self):
        assert recognized_slash_command_end("/help model") == 5

    def test_recognized_model_command(self):
        assert recognized_slash_command_end("/model") == 6

    def test_partial_command_not_highlighted(self):
        assert recognized_slash_command_end("/mod") is None

    def test_plain_text_not_highlighted(self):
        assert recognized_slash_command_end("hello") is None

    def test_stylize_slash_command(self):
        text = Text("/help model")
        stylize_slash_command(text)
        assert "cyan" in str(text._spans[0].style)
