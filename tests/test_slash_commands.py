from coding_agent.slash_commands import format_command_help, format_help_text


class TestSlashCommandHelp:
    def test_format_help_lists_all_commands(self):
        text = format_help_text()
        assert "/help" in text
        assert "/help <name>" in text
        assert "/model" in text
        assert "/model <id>" in text
        assert "/status" in text
        assert "/sessions" in text
        assert "/resume <id>" in text
        assert "/new" in text
        assert "/clear" in text
        assert "/rm <id>" in text
        assert "exit" in text
        assert "/help model" in text

    def test_format_command_help_model(self):
        text = format_command_help("model")
        assert text is not None
        assert "/model" in text
        assert "/model <id>" in text
        assert "provider API" in text

    def test_format_command_help_accepts_slash_prefix(self):
        text = format_command_help("/model")
        assert text is not None
        assert "Switch model" in text or "/model <id>" in text

    def test_format_command_help_unknown(self):
        assert format_command_help("foo") is None


class TestClearCommand:
    def test_clear_resets_session_like_new(self, tmp_workdir):
        import io

        from coding_agent.config import Config
        from coding_agent.session import SessionState
        from coding_agent.slash_commands import handle_slash_command
        from coding_agent.tui.messages import Message, MessageRole

        config = Config(
            api_key="test-key",
            model="gpt-4o-mini",
            base_url="https://example.com/v1",
            max_steps=5,
            working_dir=tmp_workdir,
        )
        session = SessionState(
            session_id="old123",
            current_model="gpt-4o-mini",
            display_messages=[Message(MessageRole.USER, "hello")],
        )
        buffer = io.StringIO()
        outcome = handle_slash_command("/clear", session, config, stream=buffer)
        assert outcome.handled is True
        assert outcome.reset_agent is True
        assert session.session_id != "old123"
        assert session.display_messages == []


class TestStatusCommand:
    def test_format_status_includes_fields(self, tmp_workdir):
        from coding_agent.config import Config
        from coding_agent.session import SessionState
        from coding_agent.slash_commands import format_status
        from coding_agent.tui.run_phase import RunPhase

        config = Config(
            api_key="test-key",
            model="gpt-4o-mini",
            base_url="https://example.com/v1",
            max_steps=15,
            working_dir=tmp_workdir,
            request_timeout=90,
        )
        session = SessionState(session_id="abc123", current_model="gpt-4o-mini")
        text = format_status(session, config, run_phase=RunPhase.IDLE)
        assert "abc123" in text
        assert "gpt-4o-mini" in text
        assert "https://example.com/v1" in text
        assert "Phase: idle" in text
        assert "sk-" not in text

    def test_format_status_accepts_string_phase(self, tmp_workdir):
        from coding_agent.config import Config
        from coding_agent.session import SessionState
        from coding_agent.slash_commands import format_status

        config = Config(
            api_key="test-key",
            model="gpt-4o-mini",
            base_url="https://example.com/v1",
            max_steps=15,
            working_dir=tmp_workdir,
        )
        session = SessionState(session_id="abc123", current_model="gpt-4o-mini")
        text = format_status(session, config, run_phase="running")
        assert "Phase: running" in text
