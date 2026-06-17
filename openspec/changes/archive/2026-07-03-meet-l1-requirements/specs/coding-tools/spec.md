## ADDED Requirements

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
