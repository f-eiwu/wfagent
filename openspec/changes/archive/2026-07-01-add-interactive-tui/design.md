## Context

Interactive mode today uses `prompt_toolkit` for a single-line `task>` prompt. User messages and agent replies are printed as separate stdout/stderr lines with no scrollback. Session status (model, cwd) prints once at startup in dim text. Slash commands (`/model`, `/help`) print to stderr. Agent step progress prints brief summaries to stderr during each turn.

The target UX (modern coding agent screenshot) has:
- **Header** — product name, version/build id, optional hint line
- **Conversation** — prior turns visible; user input in a gray bar; assistant text below
- **Input** — bottom-fixed field with `→` prefix and "Add a follow-up" placeholder
- **Footer** — model name, optional usage metric, working directory path

## Goals / Non-Goals

**Goals:**

- Full-screen TUI on TTY when running `coding-agent` without `--task`
- Scrollable conversation history for the session
- Distinct visual treatment for user vs assistant messages
- Bottom input supporting slash commands with existing cyan highlighting behavior
- Status footer showing current model and `working_dir`
- Agent step progress visible in the conversation area (e.g. dim "thinking" / tool-call lines)
- Slash-command results rendered in the log, not stderr
- Plain fallback for non-TTY, tests, and `CODING_AGENT_PLAIN_PROMPT=1`

**Non-Goals:**

- TUI for one-shot `--task` mode
- Mouse support, split panes, or file-tree sidebar
- Streaming token-by-token rendering (final reply per turn is enough for v1)
- Persisting conversation history across sessions
- Replicating the editor's `/skills` or cloud-specific features
- Windows Terminal image/emoji rendering guarantees

## Decisions

### 1. Use a TUI library for the interactive UI

**Decision:** Add `textual>=0.40` and build the interactive app as a `textual.app.App` subclass.

**Rationale:** The TUI library provides layout (header/body/footer), scrollable containers, input widgets, and theming — a good match for modern coding agent's structure. `prompt_toolkit` remains for plain-mode fallback input.

**Alternatives considered:**
- **fullscreen prompt UI** — possible but more manual layout work
- **live console rendering** — not a true interactive app; poor input handling
- **curses directly** — too low-level for maintainability

### 2. Conversation as an append-only message list

**Decision:** Maintain `list[Message]` in app state where `Message` has `role: user | assistant | system` and `text: str`. The conversation pane renders from this list on each append.

**Rationale:** Simple, testable, no widget-per-message complexity for v1. System role covers slash output, errors, and step progress.

### 3. Agent progress via callback

**Decision:** Add an optional `on_step: Callable[[str], None]` to `Agent.run()` (or a thin wrapper) that the TUI uses to append dim system lines like `→ read_file(path)`.

**Rationale:** Keeps agent core decoupled; plain CLI can keep printing to stderr via the same hook.

### 4. Module layout

```
src/coding_agent/tui/
  __init__.py
  app.py          # CodingAgentApp(TUI App)
  widgets.py      # ConversationPane, StatusFooter (if needed)
  messages.py     # Message dataclass, formatting helpers
```

`cli.py` calls `run_tui(config, session)` when TTY + not plain; otherwise existing while-loop.

### 5. Plain mode escape hatch

**Decision:** Honor existing `CODING_AGENT_PLAIN_PROMPT=1` and add `--plain` CLI flag. Also auto-fallback when `stdin` or `stdout` is not a TTY (same conditions as today).

**Rationale:** Preserves pytest ergonomics and scripted use without a terminal emulator.

### 6. Exit behavior

**Decision:** User types `exit` or `/exit` in the input, or presses Ctrl+C / Ctrl+Q. TUI quits cleanly with exit code 0.

**Rationale:** Matches current `exit` keyword; The TUI handles Ctrl+C.

### 7. Visual styling (approximate modern coding agent)

| Region | Style |
|--------|-------|
| Header | Bold title "Coding Agent", dim version string, dim hint about `/help` |
| User message | Full-width bar, dark gray background, white text |
| Assistant message | Plain text below user bar, no background |
| System/progress | Dim italic prefix `→` |
| Input | Dark bar, `→` prompt glyph, placeholder "Add a follow-up" |
| Footer | Dim `model · cwd` (usage % omitted in v1 unless cheap to add) |

Use TUI CSS (`*.tcss`) for theme; default dark theme.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| The TUI library adds dependency weight | Single well-maintained dep; plain mode needs no TUI import at module load if lazy-imported |
| TUI tests flaky in CI | Run tests with `CODING_AGENT_PLAIN_PROMPT=1`; separate optional TUI pilot test marked `@pytest.mark.tui` |
| Windows terminal compatibility | Test on Windows Terminal; document minimum terminal; plain fallback always available |
| Slash commands in multiline input | v1 stays single-line input (same as today) |
| Long responses overflow memory | Scrollable pane; no truncation in v1 beyond existing agent limits |

## Migration Plan

Additive change. Interactive TTY users get TUI automatically. Scripts and tests set plain mode. No config file migration.

## Open Questions

- Whether to show agent version from `importlib.metadata.version("coding-agent")` in header (recommended yes)
- Future: optional `--no-tui` alias for `--plain` if users prefer explicit naming
