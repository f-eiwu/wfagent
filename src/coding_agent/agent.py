import logging
from collections.abc import Callable
from typing import Any

from coding_agent.confirmation import ApprovalPrompt, format_prompt_summary, require_approval
from coding_agent.config import Config
from coding_agent.display import truncate_summary
from coding_agent.llm import LLMClient
from coding_agent.operation_allowlist import OperationAllowlist
from coding_agent.tools.factory import create_default_registry
from coding_agent.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

ToolEventCallback = Callable[[str, str], None]
StreamChunkCallback = Callable[[str], None]


class Agent:
    def __init__(
        self,
        config: Config,
        llm: LLMClient | None = None,
        tools: ToolRegistry | None = None,
        messages: list[dict[str, Any]] | None = None,
        allowlist: OperationAllowlist | None = None,
        approval_prompt: ApprovalPrompt | None = None,
    ) -> None:
        self._config = config
        self._llm = llm or LLMClient(config)
        self._tools = tools or create_default_registry(config.working_dir)
        self._allowlist = allowlist or OperationAllowlist()
        self._approval_prompt = approval_prompt
        if messages:
            self._messages = list(messages)
        else:
            self._messages = [
                {"role": "system", "content": self._build_system_prompt()}
            ]

    @property
    def messages(self) -> list[dict[str, Any]]:
        return self._messages

    def _build_system_prompt(self) -> str:
        approval_note = (
            "All file and shell operations run without confirmation."
            if self._config.auto_approve
            else (
                "Shell commands and file writes/edits require user approval before execution."
            )
        )
        return (
            "You are a coding assistant. You help users complete software tasks "
            "by reading, searching, editing, and writing files and running shell commands.\n"
            f"Your working directory is: {self._config.working_dir}\n"
            f"{approval_note}\n"
            "All file paths are relative to this directory. "
            "When the task is complete, respond with a final summary and do not "
            "request more tools."
        )

    def run(
        self,
        task: str,
        on_step: Callable[[str], None] | None = None,
        on_tool_call: ToolEventCallback | None = None,
        on_tool_result: ToolEventCallback | None = None,
        on_tool_rejected: ToolEventCallback | None = None,
        on_stream_chunk: StreamChunkCallback | None = None,
    ) -> str:
        self._messages.append({"role": "user", "content": task})

        for step in range(1, self._config.max_steps + 1):
            self._log_progress(step, "thinking", on_step=on_step)
            assistant_message = self._llm.chat(
                self._messages,
                tools=self._tools.get_schemas(),
                on_stream_chunk=on_stream_chunk,
            )
            self._messages.append(assistant_message)

            tool_calls = assistant_message.get("tool_calls")
            if not tool_calls:
                return assistant_message.get("content") or ""

            for tool_call in tool_calls:
                name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]
                summary = format_prompt_summary(name, arguments)
                if on_tool_call is not None:
                    on_tool_call(name, summary)
                self._log_progress(step, name, on_step=on_step)
                result = self._execute_tool(
                    name,
                    arguments,
                    on_tool_rejected=on_tool_rejected,
                )
                if on_tool_result is not None:
                    on_tool_result(name, truncate_summary(result))
                self._messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result,
                    }
                )

        return f"Step limit of {self._config.max_steps} reached without a final answer."

    def _execute_tool(
        self,
        name: str,
        arguments: str,
        *,
        on_tool_rejected: ToolEventCallback | None = None,
    ) -> str:
        approved, message = require_approval(
            name,
            arguments,
            self._allowlist,
            prompt_fn=self._approval_prompt,
            auto_approve=self._config.auto_approve,
        )
        if not approved:
            summary = format_prompt_summary(name, arguments)
            if on_tool_rejected is not None:
                on_tool_rejected(name, message or f"rejected {summary}")
            return message
        return self._tools.dispatch(name, arguments)

    def _log_progress(
        self,
        step: int,
        action: str,
        *,
        on_step: Callable[[str], None] | None = None,
    ) -> None:
        message = f"[step {step}] {action}"
        if on_step is not None:
            on_step(message)
            return
        logger.info(message)
