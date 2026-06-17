## Why

The interactive CLI prints a plain `task>` prompt with responses on stdout and meta-output on stderr. This feels unlike modern agent UIs (e.g. modern coding agent) where conversation history, user input, model context, and working directory are visible in one cohesive terminal layout. A TUI makes multi-turn sessions easier to follow and signals that the tool is an interactive agent, not a one-line shell command.

## What Changes

- Replace the default interactive loop with a full-screen terminal UI modeled on modern coding agent
- Show a scrollable conversation log: user turns in highlighted blocks, assistant replies below
- Add a persistent bottom input with placeholder text (e.g. "Add a follow-up") and slash-command highlighting
- Add a status footer with active model, working directory, and optional step/progress indicator
- Render slash-command output and agent step progress inside the TUI instead of stderr
- Keep one-shot `--task` mode unchanged (non-TUI)
- Provide `CODING_AGENT_PLAIN_PROMPT=1` (or `--plain`) to fall back to the current text prompt for CI, pipes, and tests

## Capabilities

### New Capabilities

- `interactive-tui`: Full-screen interactive layout — header, conversation pane, input area, status footer, and in-TUI rendering of messages and progress

### Modified Capabilities

- `cli`: Interactive mode launches the TUI by default on a TTY; startup hints and session status move into the TUI chrome; plain mode remains available via env/flag

## Impact

- `src/coding_agent/cli.py` — branch interactive mode into TUI vs plain
- New `src/coding_agent/tui/` package (app, widgets, conversation model)
- `src/coding_agent/interactive_prompt.py` — plain-mode fallback only, or absorbed into TUI input widget
- `src/coding_agent/agent.py` — optional progress callback for in-TUI step updates
- `pyproject.toml` — add TUI dependency (e.g. `textual`)
- `tests/` — TUI smoke tests with plain-mode fallback; existing CLI tests keep using plain mode
- `README.md` — screenshots/description of interactive TUI and plain fallback
