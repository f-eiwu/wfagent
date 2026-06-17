import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    func: Callable[..., str]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in self._tools.values()
        ]

    def dispatch(self, name: str, arguments: str) -> str:
        if name not in self._tools:
            return f"Error: tool '{name}' not found"

        try:
            args = json.loads(arguments) if arguments else {}
        except json.JSONDecodeError as exc:
            return f"Error: invalid JSON arguments: {exc}"

        try:
            return self._tools[name].func(**args)
        except TypeError as exc:
            return f"Error: invalid arguments for tool '{name}': {exc}"
        except Exception as exc:
            return f"Error executing tool '{name}': {exc}"
