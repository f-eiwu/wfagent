## ADDED Requirements

### Requirement: Read file tool

The agent SHALL provide a `read_file` tool that reads the contents of a file relative to the working directory and returns them as a string.

#### Scenario: Read an existing file

- **WHEN** the agent calls `read_file` with path `src/main.py` and the file exists
- **THEN** the tool returns the file contents

#### Scenario: File not found

- **WHEN** the agent calls `read_file` with a path that does not exist
- **THEN** the tool returns an error message indicating the file was not found

#### Scenario: Large file truncation

- **WHEN** the agent calls `read_file` on a file exceeding the line limit (default 500 lines)
- **THEN** the tool returns the first 500 lines and a notice that the file was truncated

### Requirement: Write file tool

The agent SHALL provide a `write_file` tool that writes content to a file relative to the working directory, creating parent directories if needed.

#### Scenario: Write a new file

- **WHEN** the agent calls `write_file` with path `output.txt` and content `hello`
- **THEN** the file is created with the given content and the tool returns a success message

#### Scenario: Overwrite existing file

- **WHEN** the agent calls `write_file` on an existing file
- **THEN** the file content is replaced and the tool returns a success message

### Requirement: List directory tool

The agent SHALL provide a `list_dir` tool that lists files and subdirectories in a directory relative to the working directory.

#### Scenario: List root working directory

- **WHEN** the agent calls `list_dir` with path `.`
- **THEN** the tool returns a list of file and directory names in the working directory

#### Scenario: List subdirectory

- **WHEN** the agent calls `list_dir` with path `src`
- **THEN** the tool returns a list of entries in the `src` subdirectory

### Requirement: Run shell command tool

The agent SHALL provide a `run_shell` tool that executes a shell command in the working directory and returns stdout, stderr, and exit code.

#### Scenario: Successful command

- **WHEN** the agent calls `run_shell` with command `echo hello`
- **THEN** the tool returns stdout `hello\n`, empty stderr, and exit code 0

#### Scenario: Failed command

- **WHEN** the agent calls `run_shell` with a command that exits non-zero
- **THEN** the tool returns the exit code and any stderr output

#### Scenario: Command timeout

- **WHEN** the agent calls `run_shell` with a command that runs longer than the timeout (default 30 seconds)
- **THEN** the tool kills the process and returns a timeout error message

### Requirement: Path traversal protection

All file tools SHALL reject paths that resolve outside the configured working directory.

#### Scenario: Path traversal attempt

- **WHEN** the agent calls any file tool with path `../../etc/passwd`
- **THEN** the tool returns an error message indicating the path is outside the working directory

### Requirement: Tool registry

Tools SHALL be registered in a central registry that provides chat-completions-compatible tool schema definitions and dispatches tool calls by name.

#### Scenario: Dispatch tool call by name

- **WHEN** the LLM requests a tool call with name `read_file` and arguments `{"path": "README.md"}`
- **THEN** the registry invokes the `read_file` implementation and returns the result

#### Scenario: Unknown tool name

- **WHEN** the LLM requests a tool call with an unrecognized name
- **THEN** the registry returns an error message indicating the tool was not found
