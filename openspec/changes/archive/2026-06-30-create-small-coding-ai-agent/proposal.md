## Why

This repository is a greenfield project with no application code yet. We need a minimal, self-contained coding AI agent that can accept natural-language tasks, reason about a codebase, and take concrete actions (read/write files, run commands) to complete them. A small agent is the right starting point: it establishes the core loop and tool surface area without the complexity of a full IDE integration or multi-agent orchestration.

## What Changes

- Add a CLI entry point to run the coding agent against a working directory
- Implement an agent loop: send user task + context to an LLM, parse tool calls, execute tools, feed results back until the task is done or a step limit is reached
- Provide built-in coding tools: read file, write file, list directory, run shell command
- Support configurable LLM provider via environment variables (API key, model name, base URL)
- Add project scaffolding: dependency manifest, basic README with setup and usage instructions
- Add a simple test suite for tool execution and agent loop behavior (mocked LLM)

## Capabilities

### New Capabilities

- `agent-core`: Core agent orchestration — conversation history, LLM interaction, tool-call parsing, step limits, and completion detection
- `coding-tools`: Built-in tools the agent can invoke against the local filesystem and shell
- `cli`: Command-line interface to start a session, pass a one-shot task, and configure the working directory

### Modified Capabilities

_(none — no existing specs)_

## Impact

- **New codebase**: Python project with `src/` layout, `pyproject.toml`, and CLI entry point
- **Dependencies**: chat-completions-compatible LLM client library (e.g., `openai`), CLI framework (e.g., `typer` or `click`)
- **External services**: Requires an LLM API key (LLM provider, cloud LLM provider, or any chat-completions-compatible endpoint)
- **Security**: Shell and file-write tools operate on the user's machine; the agent must run in a user-specified working directory with no sandbox beyond OS permissions
