## Purpose

File and directory tools available to the coding agent.

## Requirements

### Requirement: Read file tool

The agent SHALL provide a `read_file` tool that reads the contents of a file relative to the working directory and returns them as a string. The tool SHALL reject sensitive file paths and apply output redaction before returning content.

#### Scenario: Read an existing file

- **WHEN** the agent calls `read_file` with path `src/main.py` and the file exists
- **THEN** the tool returns the file contents

#### Scenario: File not found

- **WHEN** the agent calls `read_file` with a path that does not exist
- **THEN** the tool returns an error message indicating the file was not found

#### Scenario: Large file truncation

- **WHEN** the agent calls `read_file` on a file exceeding the line limit (default 500 lines)
- **THEN** the tool returns the first 500 lines and a notice that the file was truncated

#### Scenario: Sensitive file blocked

- **WHEN** the agent calls `read_file` with path `.env`
- **THEN** the tool returns an error indicating the path is blocked by security policy

### Requirement: Write file tool

The agent SHALL provide a `write_file` tool that writes content to a file relative to the working directory, creating parent directories if needed. The tool SHALL reject sensitive file paths.

#### Scenario: Write a new file

- **WHEN** the agent calls `write_file` with path `output.txt` and content `hello`
- **THEN** the file is created with the given content and the tool returns a success message

#### Scenario: Overwrite existing file

- **WHEN** the agent calls `write_file` on an existing file
- **THEN** the file content is replaced and the tool returns a success message

#### Scenario: Sensitive file write blocked

- **WHEN** the agent calls `write_file` with path `.env` and any content
- **THEN** the tool returns an error indicating the path is blocked by security policy

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

All file tools SHALL reject paths that resolve outside the configured working directory, including paths that escape via symbolic links.

#### Scenario: Path traversal attempt

- **WHEN** the agent calls any file tool with path `../../etc/passwd`
- **THEN** the tool returns an error message indicating the path is outside the working directory

#### Scenario: Symlink escape attempt

- **WHEN** the agent calls any file tool with a path that is a symlink pointing outside the working directory
- **THEN** the tool returns an error message indicating the path is outside the working directory

### Requirement: Glob files tool

The agent SHALL provide a `glob_files` tool that returns paths matching a glob pattern relative to the working directory.

#### Scenario: Match Python files

- **WHEN** the agent calls `glob_files` with pattern `**/*.py` and path `.`
- **THEN** the tool returns a list of matching relative file paths under the working directory

#### Scenario: No matches

- **WHEN** the agent calls `glob_files` with a pattern that matches nothing
- **THEN** the tool returns an empty-result message

#### Scenario: Path outside working directory blocked

- **WHEN** the agent calls `glob_files` with path `../outside`
- **THEN** the tool returns a path security error

### Requirement: Search code tool

The agent SHALL provide a `search_code` tool that searches file contents under a directory for a pattern and returns matching file paths with line numbers and snippets.

#### Scenario: Find text in codebase

- **WHEN** the agent calls `search_code` with pattern `def main` and path `.`
- **THEN** the tool returns matches with file path, line number, and a short line snippet

#### Scenario: Match limit

- **WHEN** a search would return more than the configured maximum matches
- **THEN** the tool returns the first N matches and a truncation notice

### Requirement: Edit file tool

The agent SHALL provide an `edit_file` tool that replaces a single occurrence of `old_string` with `new_string` in a file relative to the working directory. The tool SHALL be confirm-tier (same approval policy as `write_file`).

#### Scenario: Successful single replacement

- **WHEN** the agent calls `edit_file` with path `foo.py`, a unique `old_string`, and `new_string`
- **THEN** the file is updated and the tool returns a success message

#### Scenario: Old string not found

- **WHEN** the agent calls `edit_file` and `old_string` does not appear in the file
- **THEN** the tool returns an error and does not modify the file

#### Scenario: Ambiguous old string

- **WHEN** `old_string` appears more than once in the file
- **THEN** the tool returns an error indicating ambiguous match

### Requirement: Output redaction

File read results SHALL have likely secrets redacted (API keys, bearer tokens, password assignments) before being returned to the LLM.

#### Scenario: API key redacted in file content

- **WHEN** the agent reads a file containing `OPENAI_API_KEY=sk-abc123`
- **THEN** the returned content contains `[REDACTED]` instead of the key value

### Requirement: Tool registry

Tools SHALL be registered in a central registry that provides chat-completions-compatible tool schema definitions and dispatches tool calls by name.

#### Scenario: Dispatch tool call by name

- **WHEN** the LLM requests a tool call with name `read_file` and arguments `{"path": "README.md"}`
- **THEN** the registry invokes the `read_file` implementation and returns the result

#### Scenario: Unknown tool name

- **WHEN** the LLM requests a tool call with an unrecognized name
- **THEN** the registry returns an error message indicating the tool was not found
