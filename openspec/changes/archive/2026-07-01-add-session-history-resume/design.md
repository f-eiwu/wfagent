## Context

Interactive mode keeps all state in memory. `SessionState` holds only `current_model` and input-line history. The TUI maintains a separate `list[Message]` for display. Each task instantiates a new `Agent` with a fresh `_messages` list containing only the system prompt — prior turns are invisible to the LLM even though the TUI shows them.

The project already uses `.ai_history/logs/` for curated agent session logs (markdown). Session persistence will use a sibling directory `.ai_history/sessions/` for structured JSON session files scoped by working directory.

modern coding agent saves chats locally and lets users resume with full scrollback and context. This change closes the gap deferred as a non-goal in the TUI design.

## Goals / Non-Goals

**Goals:**

- Persist interactive session state to disk and restore on `--resume`, `--continue`, or `/resume`
- Reuse LLM message history across follow-up tasks within one session
- Auto-save after each turn and on graceful exit
- List sessions via `/sessions`; start fresh via `/new`
- Restore TUI conversation scrollback on resume
- Show short session id in footer / plain status line
- Ignore session files in git (user-local data)

**Non-Goals:**

- Cloud sync or multi-machine session sharing
- Session files for one-shot `--task` mode
- Encrypting session files at rest
- Pruning old sessions automatically (manual delete is fine for v1)
- Cross-working-directory session resume (sessions are keyed by `working_dir`)
- Migrating `.ai_history/logs/session.md` into structured session files
- Streaming partial responses into session files mid-run

## Decisions

### 1. JSON session files under `.ai_history/sessions/`

**Decision:** One file per session: `.ai_history/sessions/<id>.json` where `<id>` is an 8-character hex prefix of a UUID.

**Rationale:** Human-readable, easy to list and delete, aligns with existing `.ai_history/` convention. JSON supports nested LLM messages without a new dependency.

**Alternatives considered:**
- **SQLite** — better for queries but heavier for a small CLI tool
- **Single sessions index file** — corruption risk; harder to resume one session

### 2. Session file schema (v1)

```json
{
  "version": 1,
  "id": "a1b2c3d4",
  "title": "fix the login bug",
  "created_at": "2026-06-30T12:00:00Z",
  "updated_at": "2026-06-30T12:05:00Z",
  "working_dir": "/abs/path/to/project",
  "current_model": "gpt-4o-mini",
  "display_messages": [{"role": "user", "text": "..."}, ...],
  "agent_messages": [{"role": "system", "content": "..."}, ...],
  "input_history": ["prior line 1", ...]
}
```

`display_messages` mirrors TUI `Message` roles (`user`, `assistant`, `system`). `agent_messages` is the raw LLM provider-style list used by `Agent` / `LLMClient`.

### 3. Extend `SessionState` as the in-memory source of truth

**Decision:** Add `session_id`, `title`, `display_messages`, `agent_messages`, and timestamps to `SessionState` (or a composed `PersistedSession` loaded into it). `SessionStore` module handles load/save/list only.

**Rationale:** Keeps slash commands and TUI working against one object; store layer stays thin.

### 4. Session-scoped `Agent` instance in interactive mode

**Decision:** Create one `Agent` per interactive session (or pass `initial_messages` and read back `agent.messages` after each run). Interactive loop reuses the same agent message list; one-shot mode keeps creating ephemeral agents.

**Rationale:** Minimal API change: add optional `messages: list | None` to `Agent.__init__` and a `messages` property. After `run()`, caller persists updated list.

**Alternatives considered:**
- **Agent owns persistence** — couples core to filesystem
- **Rebuild messages from display_messages** — loses tool-call detail

### 5. Auto-save hook in interactive loop

**Decision:** `save_session(session, config)` called from:
- plain loop after each handled line (task complete or slash that mutates state)
- TUI after `_run_task` completes and after `/new` / `/resume`
- `atexit` or explicit save in exit handlers (plain break, TUI `exit`)

**Rationale:** Simple, no background thread; acceptable latency for small JSON files.

### 6. Session listing scoped by working directory

**Decision:** Filter session files where `working_dir` matches the resolved `config.working_dir` (normalized absolute path). Sort by `updated_at` descending.

**Rationale:** Matches how users think about project-scoped chats. Avoids showing sessions from other repos when cwd differs.

### 7. CLI flags and validation

**Decision:**
- `--resume <id>` — load session; error if not found; incompatible with `--task`
- `--continue` — load latest for cwd; if none, start new and print notice
- Mutually exclusive: `--resume` and `--continue`

Short id matching: accept full id or unique prefix if unambiguous; otherwise require full id.

### 8. Slash commands

| Command | Behavior |
|---------|----------|
| `/sessions` | List sessions for cwd |
| `/resume <id>` | Load session, refresh UI / plain context |
| `/new` | New id, empty messages, save immediately |

Update `/help` output to mention these.

### 9. Title generation

**Decision:** Set `title` from first non-slash, non-empty user task (max 80 chars). Never overwrite once set.

### 10. Gitignore

**Decision:** Add `.ai_history/sessions/` to `.gitignore` (keep `.ai_history/logs/` tracked or as today).

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Large session files from long tool-heavy runs | v1 accepts size; future pruning or tool-result truncation |
| Corrupt JSON breaks resume | Validate on load; print error and offer new session |
| LLM context window exceeded on long sessions | Document limitation; future `/compact` or summarization out of scope |
| Concurrent writes from two CLI instances | v1: last write wins; document single-instance expectation |
| `working_dir` move breaks session association | Store absolute path; sessions won't appear if cwd changes (acceptable v1) |
| Secrets in agent_messages (tool output) | Same trust model as local chat logs; gitignored directory |

## Migration Plan

Additive. Existing users get auto-created session files on first interactive run. No config migration. Plain and TUI tests use temp dirs for `.ai_history/sessions/`.

## Open Questions

- Whether to show session title in TUI header (recommended: footer id only for v1, title in `/sessions` list)
- Prefix match for short ids: implement simple longest-prefix match with ambiguity error
- Optional env `CODING_AGENT_SESSIONS_DIR` override (defer unless needed)
