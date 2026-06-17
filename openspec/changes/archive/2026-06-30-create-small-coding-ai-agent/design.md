## Context

This is a greenfield Python project. The goal is a minimal coding AI agent: a CLI program that accepts a natural-language task, calls an LLM with tool definitions, executes tool calls against the local filesystem and shell, and loops until the task is complete or a step limit is reached.

Constraints:
- Must work with any chat-completions-compatible API (LLM provider, cloud, local models via local LLM server/local LLM app)
- Must be small enough to understand in one sitting (~500–800 lines)
- No IDE integration, no web UI, no multi-agent orchestration in v1

## Goals / Non-Goals

**Goals:**
- Runnable CLI agent with `read_file`, `write_file`, `list_dir`, and `run_shell` tools
- Clean separation: CLI → Agent → Tools → LLM provider
- Configurable via environment variables and CLI flags
- Basic tests with mocked LLM responses

**Non-Goals:**
- Sandboxing or permission prompts (user trusts the agent with their working directory)
- Streaming output to the terminal (v1 can print step summaries after each iteration)
- Persistent conversation sessions across CLI invocations
- Plugin system for custom tools
- RAG / codebase indexing

## Decisions

### 1. Language: Python 3.11+

**Rationale:** Fast to prototype, excellent LLM SDK support (`openai` package), good subprocess/file APIs. The project has no existing stack to match.

**Alternatives considered:** TypeScript (better for future web UI, but heavier setup for a CLI-only v1).

### 2. LLM integration: LLM provider function-calling via `openai` SDK

**Rationale:** The chat completions API with `tools` parameter is the de-facto standard. The `openai` Python SDK supports custom `base_url`, making it compatible with cloud, local LLM server, and other providers.

**Alternatives considered:** LangChain/LlamaIndex (too heavy for a "small" agent), raw HTTP (more boilerplate).

### 3. Agent loop: synchronous step loop with max iterations

```
User task → [LLM call] → tool calls? → execute tools → append results → repeat
                      ↓ no tools
                   final answer → done
```

**Rationale:** Simple to implement and debug. A `max_steps` config (default 20) prevents runaway loops.

### 4. Tool schema: JSON Schema definitions passed to the LLM

Each tool is a Python function with a name, description, and parameters dict. Tools are registered in a `ToolRegistry` and serialized to LLM provider tool format at runtime.

**Rationale:** Keeps tool definitions co-located with implementations; easy to add new tools later.

### 5. Project layout

```
coding-agent/
├── pyproject.toml
├── README.md
├── src/
│   └── coding_agent/
│       ├── __init__.py
│       ├── __main__.py      # python -m coding_agent
│       ├── cli.py           # typer CLI
│       ├── agent.py         # Agent loop
│       ├── llm.py           # LLM client wrapper
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── registry.py
│       │   ├── file_tools.py
│       │   └── shell_tools.py
│       └── config.py        # env/flag resolution
└── tests/
    ├── test_agent.py
    ├── test_tools.py
    └── test_cli.py
```

### 6. CLI framework

**Rationale:** Lightweight, built on Click, good `--help` generation, type-hint driven.

### 7. Configuration precedence

CLI flags > environment variables > defaults.

| Setting | Env var | Default |
|---------|---------|---------|
| API key | `OPENAI_API_KEY` | (required) |
| Model | `OPENAI_MODEL` | `gpt-4o-mini` |
| Base URL | `OPENAI_BASE_URL` | `https://api.openai.com/v1` |
| Max steps | — | `20` (CLI flag `--max-steps`) |
| Working dir | — | current directory (CLI flag `--cwd`) |

### 8. Path safety

All file tool paths are resolved relative to the configured working directory. Paths that escape the working directory (via `..` traversal) are rejected.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| LLM generates destructive shell commands | Document risk clearly; v1 has no sandbox. User specifies `--cwd` to limit scope. |
| Runaway agent loops burning API credits | `max_steps` hard limit; log each step to stdout |
| Non-LLM providers may not support function calling well | Document tested providers; allow fallback to text-based tool parsing in future |
| Large files blow up context window | `read_file` truncates output beyond a configurable line limit (default 500 lines) |
| API key in environment | Standard practice; never log the key |

## Migration Plan

N/A — greenfield project. First release is `pip install -e .` from the repo root.

## Open Questions

- Should v1 support interactive REPL mode (multi-turn within one process) or only one-shot `--task` flag? **Decision: support both** — one-shot via `--task`, interactive via omitting `--task` and entering a prompt loop.
- Which model to recommend in README? **Decision: `gpt-4o-mini` as default** for cost; note that any function-calling-capable model works.
