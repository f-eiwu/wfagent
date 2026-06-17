## Context

The coding-agent CLI supports `--model` and `OPENAI_MODEL` for initial model selection. Interactive mode accepts free-text tasks only; `exit` is the sole built-in command. Users working with the chat-completions-compatible provider (`https://api.openai.com/v1`) commonly switch between models like `gpt-4o-mini` and `gpt-4o` but must restart the CLI to change models.

## Goals / Non-Goals

**Goals:**

- List curated supported models in interactive mode via `/models`
- Switch the active model mid-session via `/models <name>`
- Mark the current model clearly in the listing
- Validate model names against the curated catalog
- Keep implementation small and testable without API calls to fetch model lists

**Non-Goals:**

- Fetching models dynamically from the provider API
- Persisting model choice to disk or environment variables
- Adding slash commands for other settings (base URL, API key)
- Supporting `/models` in one-shot `--task` mode

## Decisions

### 1. Curated model catalog in code

**Decision:** Define `SUPPORTED_MODELS` as a static list in `src/coding_agent/models.py` with `(id, label)` tuples.

**Rationale:** The provider endpoint accepts a known set of provider-prefixed model IDs. A static catalog is reliable, offline-friendly, and easy to test. No extra API round-trip on `/models`.

**Alternatives considered:**
- `GET /v1/models` from provider — fragile if endpoint unsupported or slow
- User-editable config file — overkill for v1

**Initial catalog:**

| ID | Label |
|----|-------|
| `gpt-4o-mini` | GPT-4o mini (default) |
| `gpt-4o` | GPT-4o |
| `o1-mini` | o1-mini |
| `openai/gpt-4o` | GPT-4o |
| `openai/gpt-4o-mini` | GPT-4o Mini |

### 2. Session-scoped model state

**Decision:** Introduce a `SessionState` dataclass (or mutable field on a wrapper) created at interactive-mode startup. `_run_agent` receives config rebuilt with `config` + session's current model each task.

**Rationale:** Avoids mutating a frozen `Config` dataclass awkwardly; keeps one-shot mode unchanged.

### 3. Slash-command dispatch in the interactive loop

**Decision:** Before treating input as a task, check if line starts with `/`. Dispatch to a small `handle_slash_command(line, session) -> bool` that returns `True` if handled (skip agent run).

**Commands:**
- `/models` — print numbered list, highlight current with `*`
- `/models <id>` — switch if valid, else print error + hint to run `/models`
- Unknown `/foo` — print "Unknown command" with hint

**Rationale:** Extensible pattern for future slash commands without CLI subcommands (which conflict with interactive default callback).

### 4. Output to stderr

**Decision:** `/models` listing and switch confirmations print to stderr; task results stay on stdout.

**Rationale:** Consistent with step progress and security warnings.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Catalog drifts from provider offerings | Document how to extend `SUPPORTED_MODELS`; README lists models |
| User passes `--model` then switches with `/models` | Session override wins until exit; print current model on switch |
| Model ID case sensitivity | Match exactly; normalize only for lookup if we add aliases later |

## Migration Plan

No migration. New behavior is additive. Existing flags and env vars unchanged.

## Open Questions

- None blocking v1. Future: optional `OPENAI_SUPPORTED_MODELS` env override for custom catalogs.
