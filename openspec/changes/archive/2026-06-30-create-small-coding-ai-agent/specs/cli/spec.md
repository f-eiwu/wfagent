## ADDED Requirements

### Requirement: One-shot task execution

The CLI SHALL accept a `--task` flag with a natural-language task string and run the agent to completion, printing the final response.

#### Scenario: Run a one-shot task

- **WHEN** the user runs `coding-agent --task "create a hello.py file that prints hello world"`
- **THEN** the agent executes the task and prints the final response to stdout

### Requirement: Interactive mode

The CLI SHALL enter an interactive prompt loop when invoked without `--task`, allowing the user to type multiple tasks in sequence until they type `exit` or press Ctrl+C.

#### Scenario: Interactive session

- **WHEN** the user runs `coding-agent` without `--task`
- **THEN** the CLI displays a prompt, accepts task input, runs the agent, prints the result, and prompts again

#### Scenario: Exit interactive mode

- **WHEN** the user types `exit` at the interactive prompt
- **THEN** the CLI exits gracefully

### Requirement: Working directory flag

The CLI SHALL accept a `--cwd` flag to set the agent's working directory (default: current directory).

#### Scenario: Custom working directory

- **WHEN** the user runs `coding-agent --cwd /path/to/project --task "list all Python files"`
- **THEN** the agent operates on files within `/path/to/project`

### Requirement: Configuration flags

The CLI SHALL accept flags for LLM configuration: `--api-key`, `--model`, `--base-url`, and `--max-steps`.

#### Scenario: Override model via flag

- **WHEN** the user runs `coding-agent --model gpt-4o --task "explain this codebase"`
- **THEN** the agent uses `gpt-4o` for LLM calls

### Requirement: Step progress output

The CLI SHALL print a brief summary of each agent step (tool name called or "thinking") to stderr so the user can observe progress without polluting the final answer on stdout.

#### Scenario: Progress during multi-step task

- **WHEN** the agent executes a task requiring 3 tool calls
- **THEN** the CLI prints 3 step summaries to stderr and the final answer to stdout

### Requirement: Entry point

The package SHALL be invocable as `coding-agent` (console script) and as `python -m coding_agent`.

#### Scenario: Console script invocation

- **WHEN** the user runs `coding-agent --help` after installation
- **THEN** the CLI displays usage information
