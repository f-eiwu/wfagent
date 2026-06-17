from coding_agent.slash_commands import KNOWN_SLASH_COMMANDS


def recognized_slash_command_end(text: str) -> int | None:
    """Return the end index of a recognized slash command prefix, if any."""
    if not text.startswith("/"):
        return None

    space_idx = text.find(" ")
    command_end = len(text) if space_idx == -1 else space_idx
    command = text[:command_end].lower()

    if command in KNOWN_SLASH_COMMANDS:
        return command_end
    return None


def stylize_slash_command(text) -> None:
    """Apply cyan bold styling to a recognized slash command prefix in styled text."""
    from rich.text import Text

    if not isinstance(text, Text):
        return
    command_end = recognized_slash_command_end(text.plain)
    if command_end is not None:
        text.stylize("bold cyan", 0, command_end)
