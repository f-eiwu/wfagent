## MODIFIED Requirements

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

### Requirement: Path traversal protection

All file tools SHALL reject paths that resolve outside the configured working directory, including paths that escape via symbolic links.

#### Scenario: Path traversal attempt

- **WHEN** the agent calls any file tool with path `../../etc/passwd`
- **THEN** the tool returns an error message indicating the path is outside the working directory

#### Scenario: Symlink escape attempt

- **WHEN** the agent calls any file tool with a path that is a symlink pointing outside the working directory
- **THEN** the tool returns an error message indicating the path is outside the working directory

## ADDED Requirements

### Requirement: Output redaction

File read results SHALL have likely secrets redacted (API keys, bearer tokens, password assignments) before being returned to the LLM.

#### Scenario: API key redacted in file content

- **WHEN** the agent reads a file containing `OPENAI_API_KEY=sk-abc123`
- **THEN** the returned content contains `[REDACTED]` instead of the key value
