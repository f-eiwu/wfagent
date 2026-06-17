import shlex
import subprocess
from pathlib import Path

from coding_agent.security.shell_policy import is_command_allowed, needs_shell
from coding_agent.tools.registry import Tool, ToolRegistry

DEFAULT_TIMEOUT = 30


def create_shell_tools(working_dir: Path, timeout: int = DEFAULT_TIMEOUT) -> ToolRegistry:
    registry = ToolRegistry()

    def run_shell(command: str) -> str:
        if not is_command_allowed(command):
            return "Error: command is blocked by security policy"

        use_shell = needs_shell(command)
        try:
            if use_shell:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
            else:
                result = subprocess.run(
                    shlex.split(command),
                    shell=False,
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
        except subprocess.TimeoutExpired:
            return f"Error: command timed out after {timeout} seconds"
        except (OSError, ValueError) as exc:
            return f"Error executing command: {exc}"

        parts = [f"exit_code: {result.returncode}"]
        if result.stdout:
            parts.append(f"stdout:\n{result.stdout}")
        if result.stderr:
            parts.append(f"stderr:\n{result.stderr}")
        return "\n".join(parts)

    registry.register(
        Tool(
            name="run_shell",
            description="Run a shell command in the working directory.",
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"},
                },
                "required": ["command"],
            },
            func=run_shell,
        )
    )
    return registry
