import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Optional, TextIO

import typer

from coding_agent import user_io
from coding_agent.agent import Agent
from coding_agent.config import Config, ConfigError
from coding_agent.llm import LLMError
from coding_agent.interactive_prompt import read_task_input
from coding_agent.logging_config import setup_logging
from coding_agent.session import (
    SessionState,
    config_with_model,
    new_session,
    persist_session_state,
    session_from_record,
    sync_session_after_run,
)
from coding_agent.session_store import (
    AmbiguousSessionIdError,
    SessionNotFoundError,
    delete_session,
    latest_session,
    load_session,
)
from coding_agent.session_picker import pick_session, print_sessions, resolve_working_dir
from coding_agent.slash_commands import SlashOutcome, handle_slash_command
from coding_agent.tui import run_tui, should_use_tui

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="coding-agent",
    help="A small coding AI agent with LLM tool-calling.",
    add_completion=False,
)


def _store_yes_flag(ctx: typer.Context, yes: bool) -> None:
    ctx.ensure_object(dict)
    ctx.obj["auto_approve"] = yes


def _resolve_auto_approve(ctx: typer.Context, yes: bool) -> bool:
    ctx.ensure_object(dict)
    return yes or bool(ctx.obj.get("auto_approve"))


def _report_error(message: str) -> None:
    logger.error(message)
    user_io.write_line(sys.stderr, f"Error: {message}")


def _print_session_status(
    session: SessionState,
    working_dir: Path,
    *,
    stream: TextIO | None = None,
) -> None:
    out = stream or sys.stderr
    text = f"{session.session_id} · {session.current_model}\n{working_dir}"
    if getattr(out, "isatty", lambda: False)():
        user_io.write_line(out, f"\033[2m{text}\033[0m")
    else:
        user_io.write_line(out, text)


@app.command("ls")
def ls_command(
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory"),
) -> None:
    """List saved interactive sessions for the working directory."""
    print_sessions(resolve_working_dir(cwd))


def _make_agent(config: Config, session: SessionState) -> Agent:
    agent_config = config_with_model(config, session.current_model)
    messages = session.agent_messages or None
    return Agent(
        agent_config,
        messages=messages,
        allowlist=session.operation_allowlist,
    )


def _run_agent(
    config: Config,
    session: SessionState,
    task: str,
    agent: Agent,
    *,
    on_step: Callable[[str], None] | None = None,
) -> Agent:
    system_lines: list[str] = []

    def _record(line: str) -> None:
        if line.strip():
            system_lines.append(line.strip())

    def on_tool_call(_name: str, summary: str) -> None:
        _record(f"Tool call: {summary}")

    def on_tool_result(_name: str, summary: str) -> None:
        _record(f"Tool result: {_name} — {summary}")

    def on_tool_rejected(_name: str, reason: str) -> None:
        _record(f"Rejected: {reason}")

    def combined_on_step(message: str) -> None:
        _record(message)
        if on_step is not None:
            on_step(message)

    try:
        result = agent.run(
            task,
            on_step=combined_on_step,
            on_tool_call=on_tool_call,
            on_tool_result=on_tool_result,
            on_tool_rejected=on_tool_rejected,
        )
    except LLMError as exc:
        _report_error(str(exc))
        raise typer.Exit(1) from exc
    sync_session_after_run(
        session,
        agent.messages,
        user_text=task,
        assistant_text=result,
        system_lines=system_lines,
    )
    persist_session_state(session, config)
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    sys.stdout.buffer.write((result + "\n").encode(encoding, errors="replace"))
    return agent


def _run_interactive_plain(
    config: Config,
    session: SessionState,
    *,
    plain: bool,
) -> None:
    user_io.write_line(sys.stderr, "Interactive mode. Type 'exit' to quit.")
    user_io.write_line(
        sys.stderr,
        "Use /help for commands (e.g. /status, /model).",
    )
    _print_session_status(session, config.working_dir)
    agent = _make_agent(config, session)
    while True:
        try:
            user_input = read_task_input(
                plain=plain,
                history=session.get_prompt_history(),
            )
        except (EOFError, KeyboardInterrupt):
            user_io.write_line(sys.stderr)
            break
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break

        outcome = handle_slash_command(user_input, session, config)
        if outcome.handled:
            if outcome.reset_agent:
                agent = _make_agent(config, session)
                persist_session_state(session, config)
            continue

        def on_step(message: str) -> None:
            user_io.write_line(sys.stderr, message)

        agent = _run_agent(
            config,
            session,
            user_input,
            agent,
            on_step=on_step,
        )

    persist_session_state(session, config)


def _resolve_interactive_session(
    config: Config,
    *,
    resume_id: str | None,
    continue_session: bool,
) -> SessionState:
    if resume_id:
        try:
            record = load_session(config.working_dir, resume_id)
        except SessionNotFoundError as exc:
            _report_error(str(exc))
            raise typer.Exit(1) from exc
        return session_from_record(record)

    if continue_session:
        record = latest_session(config.working_dir)
        if record is None:
            user_io.write_line(
                sys.stderr,
                "No prior session found; started a new session.",
            )
            return new_session(config)
        return session_from_record(record)

    return new_session(config)


def _print_yes_warning() -> None:
    user_io.write_line(
        sys.stderr,
        "Warning: risky operations will run without confirmation.",
    )


def _load_config(
    *,
    cwd: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    max_steps: int | None = None,
    log_level: str | None = None,
    auto_approve: bool = False,
) -> Config:
    try:
        config = Config.from_sources(
            api_key=api_key,
            model=model,
            base_url=base_url,
            max_steps=max_steps,
            log_level=log_level,
            cwd=cwd,
            auto_approve=auto_approve,
        )
    except ConfigError as exc:
        _report_error(str(exc))
        raise typer.Exit(1) from exc
    setup_logging(config.log_level)
    return config


def _start_interactive(
    config: Config,
    session: SessionState,
    *,
    plain: bool,
) -> None:
    persist_session_state(session, config)
    if should_use_tui(plain=plain):
        run_tui(config, session)
        return
    _run_interactive_plain(config, session, plain=plain)


@app.command("rm")
def rm_command(
    session_id: str = typer.Argument(..., help="Session id to remove"),
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory"),
) -> None:
    """Delete a saved interactive session."""
    working_dir = resolve_working_dir(cwd)
    try:
        record = delete_session(working_dir, session_id)
    except SessionNotFoundError as exc:
        _report_error(str(exc))
        raise typer.Exit(1) from exc
    except AmbiguousSessionIdError as exc:
        _report_error(str(exc))
        raise typer.Exit(1) from exc
    user_io.write_line(sys.stdout, f"Removed session {record.id}")


@app.command("resume")
def resume_command(
    ctx: typer.Context,
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="LLM API key"),
    model: Optional[str] = typer.Option(None, "--model", help="LLM model name"),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="LLM API base URL"),
    max_steps: Optional[int] = typer.Option(None, "--max-steps", help="Max agent steps"),
    log_level: Optional[str] = typer.Option(
        None,
        "--log-level",
        help="Operational log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Allow writes and shell commands without confirmation",
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Use plain text prompt instead of the interactive TUI",
    ),
) -> None:
    """Pick a saved session interactively, then resume."""
    auto_approve = _resolve_auto_approve(ctx, yes)
    if auto_approve:
        _print_yes_warning()
    config = _load_config(
        cwd=cwd,
        api_key=api_key,
        model=model,
        base_url=base_url,
        max_steps=max_steps,
        log_level=log_level,
        auto_approve=auto_approve,
    )
    session = pick_session(config)
    _start_interactive(config, session, plain=plain)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory (default: current directory)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="LLM API key"),
    model: Optional[str] = typer.Option(None, "--model", help="LLM model name"),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="LLM API base URL"),
    max_steps: Optional[int] = typer.Option(None, "--max-steps", help="Max agent steps"),
    log_level: Optional[str] = typer.Option(
        None,
        "--log-level",
        help="Operational log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Allow writes and shell commands without confirmation",
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Use plain text prompt instead of the interactive TUI",
    ),
    resume_id: Optional[str] = typer.Option(
        None,
        "--resume",
        help="Resume a saved interactive session by id",
    ),
    continue_session: bool = typer.Option(
        False,
        "--continue",
        help="Resume the most recent saved session for the working directory",
    ),
) -> None:
    _store_yes_flag(ctx, yes)
    if ctx.invoked_subcommand is not None:
        return

    if resume_id and continue_session:
        _report_error("--resume and --continue cannot be used together.")
        raise typer.Exit(1)

    if yes:
        _print_yes_warning()

    config = _load_config(
        cwd=cwd,
        api_key=api_key,
        model=model,
        base_url=base_url,
        max_steps=max_steps,
        log_level=log_level,
        auto_approve=yes,
    )

    session = _resolve_interactive_session(
        config,
        resume_id=resume_id,
        continue_session=continue_session,
    )
    _start_interactive(config, session, plain=plain)


if __name__ == "__main__":
    app()
