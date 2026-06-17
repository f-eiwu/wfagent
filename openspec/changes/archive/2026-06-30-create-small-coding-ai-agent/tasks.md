## 1. Project Setup

- [x] 1.1 Create `pyproject.toml` with package metadata, dependencies (`openai`, `typer`), console script entry point `coding-agent`, and dev dependencies (`pytest`)
- [x] 1.2 Create `src/coding_agent/` package structure with `__init__.py` and `__main__.py`
- [x] 1.3 Create `tests/` directory with `conftest.py` providing a temporary working directory fixture

## 2. Configuration

- [x] 2.1 Implement `src/coding_agent/config.py` with a `Config` dataclass resolving API key, model, base URL, max steps, and working directory from CLI flags, env vars, and defaults
- [x] 2.2 Add validation that raises a clear error when API key is missing

## 3. Coding Tools

- [x] 3.1 Implement `src/coding_agent/tools/registry.py` with `ToolRegistry` class: register tools, generate LLM provider tool schemas, dispatch calls by name
- [x] 3.2 Implement `src/coding_agent/tools/file_tools.py` with `read_file`, `write_file`, and `list_dir` tools including path traversal protection and file truncation
- [x] 3.3 Implement `src/coding_agent/tools/shell_tools.py` with `run_shell` tool including timeout handling
- [x] 3.4 Write `tests/test_tools.py` covering happy paths, path traversal rejection, file-not-found, truncation, and command timeout

## 4. LLM Client

- [x] 4.1 Implement `src/coding_agent/llm.py` with an `LLMClient` wrapper around the LLM SDK that sends chat completions with tool definitions and returns the assistant message
- [x] 4.2 Support configurable `base_url` for chat-completions-compatible providers

## 5. Agent Core

- [x] 5.1 Implement `src/coding_agent/agent.py` with `Agent` class: system prompt construction, conversation history management, step loop (LLM call → tool execution → repeat), and max-steps enforcement
- [x] 5.2 Print step progress summaries (tool name or "thinking") during execution
- [x] 5.3 Write `tests/test_agent.py` with mocked LLM responses testing one-shot completion, multi-step tool use, and step-limit behavior

## 6. CLI

- [x] 6.1 Implement `src/coding_agent/cli.py` with a CLI app supporting `--task`, `--cwd`, `--api-key`, `--model`, `--base-url`, and `--max-steps` flags
- [x] 6.2 Implement one-shot mode (`--task`) and interactive REPL mode (no `--task`, type `exit` to quit)
- [x] 6.3 Wire `__main__.py` to invoke the CLI app
- [x] 6.4 Write `tests/test_cli.py` testing `--help` output and argument parsing (mock agent run)

## 7. Documentation and Final Verification

- [x] 7.1 Replace README.md with project-specific documentation: description, requirements (Python 3.11+, API key), installation (`pip install -e .`), usage examples, and security note about shell access
- [x] 7.2 Run full test suite (`pytest`) and verify all tests pass
- [x] 7.3 Manual smoke test: run `coding-agent --task "create a hello.py that prints hello world"` against a temp directory
