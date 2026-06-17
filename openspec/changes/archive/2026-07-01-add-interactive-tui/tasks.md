## 1. Dependencies and Scaffolding

- [x] 1.1 Add `textual>=0.40` to `pyproject.toml`
- [x] 1.2 Create `src/coding_agent/tui/` package (`__init__.py`, `messages.py`, `widgets.py`, `app.py`)
- [x] 1.3 Add `app.tcss` theme file with dark styling for header, user bar, assistant text, input, footer

## 2. Message Model and Agent Hook

- [x] 2.1 Add `Message` dataclass (`role`, `text`) and helpers in `tui/messages.py`
- [x] 2.2 Add optional `on_step: Callable[[str], None] | None` to `Agent.run()` for step progress callbacks
- [x] 2.3 Wire plain-mode CLI to use `on_step` printing to stderr (preserve existing behavior)

## 3. TUI Layout

- [x] 3.1 Implement `CodingAgentApp` with header (title, version, `/help` hint), scrollable `ConversationPane`, bottom `Input`, and `StatusFooter`
- [x] 3.2 Render user messages as full-width highlighted bars; assistant and system messages with distinct styles
- [x] 3.3 Auto-scroll conversation to latest message on append
- [x] 3.4 Show placeholder "Add a follow-up" on empty input

## 4. Interactive Logic

- [x] 4.1 On input submit: dispatch `exit`, slash commands (`handle_slash_command`), or agent task
- [x] 4.2 Append user message before agent run; append assistant reply on success; append system line on `LLMError`
- [x] 4.3 Route slash-command and step-progress output to conversation as system messages
- [x] 4.4 Update footer when model changes via `/model`
- [x] 4.5 Support Ctrl+C / agreed quit shortcut for clean exit

## 5. CLI Integration

- [x] 5.1 Add `--plain` flag to `cli.py`; extend plain detection to include `--plain`
- [x] 5.2 Add `run_tui(config, session)` entry and branch interactive loop: TUI on TTY, plain otherwise
- [x] 5.3 Lazy-import the TUI so plain mode and one-shot mode avoid loading TUI at import time
- [x] 5.4 Move startup hint into TUI header; keep stderr hint only for plain mode

## 6. Tests and Documentation

- [x] 6.1 Add `tests/test_tui_messages.py` for message formatting helpers
- [x] 6.2 Add `tests/test_tui_app.py` with plain-mode and mocked TUI tests where feasible
- [x] 6.3 Ensure existing interactive tests run with `CODING_AGENT_PLAIN_PROMPT=1`
- [x] 6.4 Update `README.md` with TUI description, screenshot placeholder, and `--plain` fallback
- [x] 6.5 Run full test suite (`pytest`) and verify all tests pass
