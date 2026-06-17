## Why

Users must set `OPENAI_MODEL` or pass `--model` before starting a session to try a different LLM. In interactive mode there is no way to discover which models work with the configured provider or switch mid-session without restarting. A `/models` slash command makes model selection discoverable and fast during coding tasks.

## What Changes

- Add `/models` slash command in interactive mode to list supported models with the current selection highlighted
- Add `/models <name>` to switch the active model for the remainder of the interactive session
- Define a curated list of supported models (provider-prefixed IDs) with sensible defaults for the chat-completions-compatible endpoint
- Persist the selected model in session state only (does not modify environment variables)
- Show clear errors for unknown model names or use outside interactive mode

## Capabilities

### New Capabilities

- `model-catalog`: Curated supported-model list, validation, and session-scoped model selection

### Modified Capabilities

- `cli`: Interactive slash commands (`/models`, `/models <name>`), session model display, and help hint on startup

## Impact

- `src/coding_agent/cli.py` — interactive loop slash-command parsing, session state
- `src/coding_agent/config.py` — supported models catalog, mutable model on Config or session wrapper
- `tests/test_cli.py` — slash command and model switching tests
- `README.md` — document `/models` usage in interactive mode
