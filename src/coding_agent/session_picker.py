from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

from coding_agent.config import Config
from coding_agent.session import SessionState, new_session, session_from_record
from coding_agent.session_store import (
    SessionNotFoundError,
    SessionRecord,
    format_sessions_table,
    list_sessions,
    resolve_session_choice,
)
from coding_agent import user_io


def resolve_working_dir(cwd: str | None = None) -> Path:
    return Path(cwd).resolve() if cwd else Path.cwd().resolve()


def print_sessions(working_dir: Path) -> list[SessionRecord]:
    sessions = list_sessions(working_dir)
    user_io.write_line(sys.stdout, format_sessions_table(sessions))
    return sessions


def pick_session(
    config: Config,
    *,
    input_fn: Callable[[str], str] | None = None,
) -> SessionState:
    sessions = list_sessions(config.working_dir)
    if not sessions:
        user_io.write_line(
            sys.stderr,
            "No saved sessions; starting a new session.",
        )
        return new_session(config)

    user_io.write_line(sys.stderr, format_sessions_table(sessions))
    user_io.write_line(
        sys.stderr,
        "Select session [1-{}], id, or n for new:".format(len(sessions)),
    )

    reader = input_fn or input
    while True:
        try:
            choice = reader("> ").strip()
        except (EOFError, KeyboardInterrupt):
            user_io.write_line(sys.stderr)
            raise SystemExit(0) from None

        if not choice or choice.lower() in {"n", "new"}:
            return new_session(config)

        try:
            record = resolve_session_choice(config.working_dir, sessions, choice)
        except SessionNotFoundError as exc:
            user_io.write_line(sys.stderr, f"Error: {exc}")
            continue

        return session_from_record(record)
