from pathlib import Path

from coding_agent.tools.file_tools import create_file_tools
from coding_agent.tools.registry import ToolRegistry
from coding_agent.tools.shell_tools import create_shell_tools


def create_default_registry(working_dir: Path) -> ToolRegistry:
    registry = ToolRegistry()
    for tool in create_file_tools(working_dir)._tools.values():
        registry.register(tool)
    for tool in create_shell_tools(working_dir)._tools.values():
        registry.register(tool)
    return registry
