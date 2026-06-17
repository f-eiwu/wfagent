## 1. Model Catalog Module

- [x] 1.1 Create `src/coding_agent/models.py` with `SUPPORTED_MODELS` list of `(id, label)` tuples
- [x] 1.2 Implement `list_models()`, `is_supported(model_id)`, and `format_models_list(current_model)` helpers
- [x] 1.3 Write `tests/test_models.py` for catalog contents, validation, and list formatting

## 2. Session State

- [x] 2.1 Add `SessionState` dataclass holding `current_model: str`
- [x] 2.2 Add `config_with_model(config, model)` helper to produce a Config copy with updated model for agent runs

## 3. Slash Command Handler

- [x] 3.1 Implement `handle_slash_command(line, session) -> bool` in `cli.py` or `slash_commands.py`
- [x] 3.2 Handle `/models` (list) and `/models <id>` (switch with validation)
- [x] 3.3 Handle unknown slash commands with a helpful error message

## 4. Interactive Loop Integration

- [x] 4.1 Initialize `SessionState` from resolved config model at interactive startup
- [x] 4.2 Dispatch slash commands before agent runs in the interactive loop
- [x] 4.3 Pass session model into `_run_agent` via `config_with_model`
- [x] 4.4 Add interactive startup hint mentioning `/models` on stderr

## 5. Tests and Documentation

- [x] 5.1 Extend `tests/test_cli.py` for `/models` list, switch, invalid switch, and no-agent-invocation
- [x] 5.2 Update README.md interactive mode section with `/models` examples
- [x] 5.3 Run full test suite (`pytest`) and verify all tests pass
