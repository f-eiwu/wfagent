from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class SessionStoreError(Exception):
    """Base error for session persistence."""


class SessionNotFoundError(SessionStoreError):
    """No session matches the given id."""


class AmbiguousSessionIdError(SessionStoreError):
    """Multiple sessions match the given id prefix."""


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_session_id() -> str:
    return uuid4().hex[:8]


def sessions_dir(working_dir: Path) -> Path:
    return working_dir.resolve() / ".ai_history" / "sessions"


def _normalize_working_dir(path: Path) -> str:
    return str(path.resolve())


@dataclass
class SessionRecord:
    version: int = 1
    id: str = ""
    title: str = ""
    created_at: str = ""
    updated_at: str = ""
    working_dir: str = ""
    current_model: str = ""
    display_messages: list[dict[str, str]] = field(default_factory=list)
    agent_messages: list[dict[str, Any]] = field(default_factory=list)
    input_history: list[str] = field(default_factory=list)
    operation_allowlist: list[list[str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionRecord:
        return cls(
            version=int(data.get("version", 1)),
            id=str(data["id"]),
            title=str(data.get("title", "")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
            working_dir=str(data.get("working_dir", "")),
            current_model=str(data.get("current_model", "")),
            display_messages=list(data.get("display_messages", [])),
            agent_messages=list(data.get("agent_messages", [])),
            input_history=list(data.get("input_history", [])),
            operation_allowlist=list(data.get("operation_allowlist", [])),
        )


def _session_path(working_dir: Path, session_id: str) -> Path:
    return sessions_dir(working_dir) / f"{session_id}.json"


def save_session(record: SessionRecord) -> None:
    root = Path(record.working_dir)
    path = _session_path(root, record.id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(record.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def _load_record_file(path: Path) -> SessionRecord:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SessionStoreError(f"Failed to read session file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SessionStoreError(f"Invalid session file {path}: expected JSON object")
    return SessionRecord.from_dict(data)


def _iter_session_files(working_dir: Path) -> list[Path]:
    directory = sessions_dir(working_dir)
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.json"))


def _matches_working_dir(record: SessionRecord, working_dir: Path) -> bool:
    return record.working_dir == _normalize_working_dir(working_dir)


def list_sessions(working_dir: Path) -> list[SessionRecord]:
    records: list[SessionRecord] = []
    for path in _iter_session_files(working_dir):
        if path.name.endswith(".json.tmp"):
            continue
        try:
            record = _load_record_file(path)
        except SessionStoreError:
            continue
        if _matches_working_dir(record, working_dir):
            records.append(record)
    records.sort(key=lambda r: r.updated_at, reverse=True)
    return records


def latest_session(working_dir: Path) -> SessionRecord | None:
    sessions = list_sessions(working_dir)
    return sessions[0] if sessions else None


def _resolve_session_path(working_dir: Path, session_id: str) -> Path:
    directory = sessions_dir(working_dir)
    exact = directory / f"{session_id}.json"
    if exact.is_file():
        return exact

    prefix = session_id.lower()
    matches = [
        path
        for path in _iter_session_files(working_dir)
        if path.stem.lower().startswith(prefix)
    ]
    if not matches:
        raise SessionNotFoundError(f"No session found for id '{session_id}'")
    if len(matches) > 1:
        ids = ", ".join(sorted(path.stem for path in matches))
        raise AmbiguousSessionIdError(
            f"Session id '{session_id}' is ambiguous; matches: {ids}"
        )
    return matches[0]


def load_session(working_dir: Path, session_id: str) -> SessionRecord:
    path = _resolve_session_path(working_dir, session_id)
    record = _load_record_file(path)
    if not _matches_working_dir(record, working_dir):
        raise SessionNotFoundError(
            f"Session '{record.id}' belongs to another working directory"
        )
    return record


def delete_session(working_dir: Path, session_id: str) -> SessionRecord:
    record = load_session(working_dir, session_id)
    path = _resolve_session_path(working_dir, record.id)
    path.unlink(missing_ok=True)
    path.with_suffix(".json.tmp").unlink(missing_ok=True)
    return record


def format_sessions_table(sessions: list[SessionRecord]) -> str:
    if not sessions:
        return "No saved sessions for this working directory."
    lines = ["Sessions:", ""]
    for index, record in enumerate(sessions, start=1):
        title = record.title or "(untitled)"
        lines.append(
            f"  {index}  {record.id}  {title}  updated={record.updated_at}"
        )
    lines.extend(
        [
            "",
            "Resume: coding-agent resume",
            "        coding-agent --resume <id>",
            "Remove: coding-agent rm <id>",
        ]
    )
    return "\n".join(lines)


def format_sessions_list(
    sessions: list[SessionRecord],
    *,
    current_id: str | None = None,
) -> str:
    if not sessions:
        return "No saved sessions for this working directory."
    lines = ["Saved sessions:", ""]
    for index, record in enumerate(sessions, start=1):
        marker = " (current)" if record.id == current_id else ""
        title = record.title or "(untitled)"
        lines.append(
            f"  {index}  {record.id}  {title}  updated={record.updated_at}{marker}"
        )
    lines.extend(
        [
            "",
            "Use /resume <id>, coding-agent resume, or coding-agent --resume <id>",
            "Remove: /rm <id> or coding-agent rm <id>",
        ]
    )
    return "\n".join(lines)


def resolve_session_choice(
    working_dir: Path,
    sessions: list[SessionRecord],
    choice: str,
) -> SessionRecord:
    text = choice.strip()
    if text.isdigit():
        index = int(text)
        if 1 <= index <= len(sessions):
            return sessions[index - 1]
        raise SessionNotFoundError(
            f"Invalid session number {index}; choose 1-{len(sessions)}"
        )
    return load_session(working_dir, text)
