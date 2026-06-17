import sys
from dataclasses import dataclass
from typing import Literal, TextIO

from coding_agent.config import Config
from coding_agent.models import ModelsFetchError, fetch_models, format_models_list, is_supported
from coding_agent.session import SessionState, persist_session_state
from coding_agent.session_store import (
    AmbiguousSessionIdError,
    SessionNotFoundError,
    delete_session,
    format_sessions_list,
    list_sessions,
    load_session,
    resolve_session_choice,
)
from coding_agent import user_io
from coding_agent.tui.run_phase import RunPhase, coerce_run_phase

KNOWN_SLASH_COMMANDS = frozenset(
    {"/help", "/model", "/status", "/sessions", "/resume", "/new", "/clear", "/rm"}
)

_COMMAND_SUMMARY: tuple[tuple[str, str], ...] = (
    ("/help", "Show available slash commands"),
    ("/help <name>", "Help for a specific command"),
    ("/model", "List models from the provider API"),
    ("/model <id>", "Switch model for this session"),
    ("/status", "Show session and runtime status"),
    ("/sessions", "List saved sessions for this project"),
    ("/resume <id>", "Resume a saved session"),
    ("/new", "Start a new session (clears conversation)"),
    ("/clear", "Alias for /new — clear conversation and start fresh"),
    ("/rm <id>", "Delete a saved session"),
)

_COMMAND_TOPICS: dict[str, tuple[str, ...]] = {
    "help": (
        "/help — Show available slash commands",
        "",
        "Usage:",
        "  /help           List all commands",
        "  /help <name>    Help for one command (e.g. /help model)",
    ),
    "model": (
        "/model — List or switch LLM models",
        "",
        "Models are fetched from your provider API (GET /v1/models).",
        "Switches apply to this session only; OPENAI_MODEL is unchanged.",
        "",
        "Usage:",
        "  /model              List available models (current shown in green)",
        "  /model <id>         Switch model (e.g. /model gpt-4o-mini)",
    ),
    "status": (
        "/status — Show session and runtime status",
        "",
        "Displays session id, model, working directory, limits, and run phase.",
        "",
        "Usage:",
        "  /status",
    ),
    "sessions": (
        "/sessions — List saved sessions",
        "",
        "Shows session id, title, and last-updated time for this working directory.",
        "",
        "Usage:",
        "  /sessions",
    ),
    "resume": (
        "/resume — Switch to a saved session",
        "",
        "Usage:",
        "  /resume <id>        Load session by id (prefix match if unique)",
    ),
    "new": (
        "/new — Start a fresh session",
        "",
        "Clears conversation history and assigns a new session id.",
        "Alias: /clear",
        "",
        "Usage:",
        "  /new",
        "  /clear",
    ),
    "clear": (
        "/clear — Clear conversation and start a fresh session",
        "",
        "Alias for /new. Clears conversation history and assigns a new session id.",
        "",
        "Usage:",
        "  /clear",
        "  /new",
    ),
    "rm": (
        "/rm — Delete a saved session",
        "",
        "Removes the session file from disk. If you delete the current session,",
        "a new session is started automatically.",
        "",
        "Usage:",
        "  /rm <id>            Delete by id (prefix match if unique)",
        "  /rm <n>             Delete by number from /sessions list",
    ),
    "exit": (
        "exit — Quit interactive mode",
        "",
        "Usage:",
        "  exit",
    ),
}


@dataclass(frozen=True)
class SlashOutcome:
    handled: bool = False
    reset_agent: bool = False


def _print_block(text: str, stream: TextIO) -> None:
    if stream is sys.stderr:
        text = "\n".join(f"  {line}" for line in text.splitlines())
    user_io.write_line(stream, text)


def _model_list_highlight(stream: TextIO) -> Literal[False, "ansi", "rich"]:
    if stream is sys.stderr:
        return "ansi" if stream.isatty() else False
    return "rich"


def _normalize_help_topic(arg: str) -> str | None:
    key = arg.lower().lstrip("/")
    if key in _COMMAND_TOPICS:
        return key
    return None


def format_help_text() -> str:
    lines = ["Interactive commands:", ""]
    for command, description in _COMMAND_SUMMARY:
        lines.append(f"  {command:<16} {description}")
    lines.extend(["", "  exit             Quit interactive mode"])
    lines.extend(["", "Run /help <name> for details (e.g. /help model)."])
    return "\n".join(lines)


def format_command_help(topic: str) -> str | None:
    normalized = _normalize_help_topic(topic)
    if normalized is None:
        return None
    return "\n".join(_COMMAND_TOPICS[normalized])


def format_status(
    session: SessionState,
    config: Config,
    *,
    run_phase: RunPhase | str = RunPhase.IDLE,
) -> str:
    auto = "yes" if config.auto_approve else "no"
    phase = coerce_run_phase(run_phase).value
    lines = [
        f"Session: {session.session_id}",
        f"Model: {session.current_model}",
        f"Working dir: {config.working_dir}",
        f"Max steps: {config.max_steps}",
        f"Base URL: {config.base_url}",
        f"Request timeout: {config.request_timeout}s",
        f"Log level: {config.log_level}",
        f"Auto-approve (-y): {auto}",
        f"Phase: {phase}",
    ]
    return "\n".join(lines)


def handle_slash_command(
    line: str,
    session: SessionState,
    config: Config,
    *,
    stream: TextIO | None = None,
    run_phase: RunPhase | str = RunPhase.IDLE,
) -> SlashOutcome:
    out = stream or sys.stderr
    stripped = line.strip()
    if not stripped.startswith("/"):
        return SlashOutcome(handled=False)

    parts = stripped.split(maxsplit=1)
    command = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if command == "/help":
        if not arg:
            user_io.write_line(out, format_help_text())
            return SlashOutcome(handled=True)
        help_text = format_command_help(arg)
        if help_text is None:
            user_io.write_line(
                out,
                f"Error: unknown help topic '{arg}'. "
                "Run /help for all commands.",
            )
            return SlashOutcome(handled=True)
        user_io.write_line(out, help_text)
        return SlashOutcome(handled=True)

    if command == "/model":
        try:
            available_models = fetch_models(config.api_key, config.base_url)
        except ModelsFetchError as exc:
            user_io.write_line(out, f"Error: {exc}")
            return SlashOutcome(handled=True)

        if not arg:
            _print_block(
                format_models_list(
                    available_models,
                    session.current_model,
                    highlight=_model_list_highlight(out),
                ),
                out,
            )
            return SlashOutcome(handled=True)
        if is_supported(arg, available_models):
            session.current_model = arg
            user_io.write_line(out, f"Switched to {arg}")
            return SlashOutcome(handled=True, reset_agent=True)
        user_io.write_line(
            out,
            f"Error: unknown model '{arg}'. Run /model to list supported models.",
        )
        return SlashOutcome(handled=True)

    if command == "/status":
        _print_block(format_status(session, config, run_phase=run_phase), out)
        return SlashOutcome(handled=True)

    if command == "/sessions":
        sessions = list_sessions(config.working_dir)
        _print_block(
            format_sessions_list(sessions, current_id=session.session_id),
            out,
        )
        return SlashOutcome(handled=True)

    if command == "/resume":
        if not arg:
            user_io.write_line(out, "Error: /resume requires a session id.")
            return SlashOutcome(handled=True)
        try:
            record = load_session(config.working_dir, arg)
        except SessionNotFoundError as exc:
            user_io.write_line(out, f"Error: {exc}")
            return SlashOutcome(handled=True)
        except AmbiguousSessionIdError as exc:
            user_io.write_line(out, f"Error: {exc}")
            return SlashOutcome(handled=True)
        session.load_from_record(record)
        persist_session_state(session, config)
        user_io.write_line(out, f"Resumed session {session.session_id}")
        return SlashOutcome(handled=True, reset_agent=True)

    if command in ("/new", "/clear"):
        session.reset_for_new(config)
        persist_session_state(session, config)
        user_io.write_line(out, f"Started new session {session.session_id}")
        return SlashOutcome(handled=True, reset_agent=True)

    if command == "/rm":
        if not arg:
            user_io.write_line(out, "Error: /rm requires a session id.")
            return SlashOutcome(handled=True)
        try:
            sessions = list_sessions(config.working_dir)
            if arg.isdigit():
                record = resolve_session_choice(config.working_dir, sessions, arg)
            else:
                record = load_session(config.working_dir, arg)
            delete_session(config.working_dir, record.id)
        except SessionNotFoundError as exc:
            user_io.write_line(out, f"Error: {exc}")
            return SlashOutcome(handled=True)
        except AmbiguousSessionIdError as exc:
            user_io.write_line(out, f"Error: {exc}")
            return SlashOutcome(handled=True)
        user_io.write_line(out, f"Removed session {record.id}")
        if record.id == session.session_id:
            session.reset_for_new(config)
            persist_session_state(session, config)
            return SlashOutcome(handled=True, reset_agent=True)
        return SlashOutcome(handled=True)

    user_io.write_line(out, f"Unknown command: {command}. Try /help.")
    return SlashOutcome(handled=True)
