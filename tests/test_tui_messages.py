from coding_agent.tui.messages import Message, MessageRole, format_step_progress, message_css_class


class TestMessages:
    def test_format_step_progress(self):
        assert format_step_progress(2, "read_file") == "→ [step 2] read_file"

    def test_message_css_class_user(self):
        assert message_css_class(MessageRole.USER) == "user-message"

    def test_message_css_class_assistant(self):
        assert message_css_class(MessageRole.ASSISTANT) == "assistant-message"

    def test_message_css_class_system(self):
        assert message_css_class(MessageRole.SYSTEM) == "system-message"

    def test_message_dataclass(self):
        msg = Message(MessageRole.USER, "hello")
        assert msg.role is MessageRole.USER
        assert msg.text == "hello"
