import logging
import time
from collections.abc import Callable
from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError, OpenAI

from coding_agent.config import Config

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 1.0


class LLMError(Exception):
    """Raised when the LLM API returns an unexpected or invalid response."""


class LLMClient:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.request_timeout,
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        on_stream_chunk: Callable[[str], None] | None = None,
    ) -> dict[str, Any]:
        if on_stream_chunk is not None:
            try:
                return self._chat_with_retry(
                    messages,
                    tools,
                    stream=True,
                    on_stream_chunk=on_stream_chunk,
                )
            except LLMError:
                logger.debug("Streaming chat with tools failed; retrying without tools")
                if tools:
                    try:
                        return self._chat_with_retry(
                            messages,
                            tools=None,
                            stream=True,
                            on_stream_chunk=on_stream_chunk,
                        )
                    except LLMError:
                        pass
                return self._chat_with_retry(
                    messages,
                    tools,
                    stream=True,
                    on_stream_chunk=on_stream_chunk,
                )
        try:
            return self._chat_with_retry(messages, tools, stream=False)
        except LLMError:
            logger.debug("Non-streaming chat with tools failed; retrying without tools")
            if tools:
                try:
                    return self._chat_with_retry(messages, tools=None, stream=False)
                except LLMError:
                    pass
            logger.debug("Retrying chat with streaming enabled")
            return self._chat_with_retry(messages, tools, stream=True)

    def _chat_with_retry(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        *,
        stream: bool,
        on_stream_chunk: Callable[[str], None] | None = None,
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                return self._chat(
                    messages,
                    tools,
                    stream=stream,
                    on_stream_chunk=on_stream_chunk,
                )
            except LLMError as exc:
                last_error = exc
                if attempt >= MAX_RETRIES or not _is_transient(exc):
                    raise
                logger.warning(
                    "LLM request failed (attempt %s/%s): %s",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    exc,
                )
                logger.debug("Retrying after %.1fs", RETRY_BACKOFF_SECONDS)
                time.sleep(RETRY_BACKOFF_SECONDS)
        raise LLMError(str(last_error)) from last_error

    def _chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        *,
        stream: bool,
        on_stream_chunk: Callable[[str], None] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self._config.model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            kwargs["tools"] = tools

        try:
            response = self._client.chat.completions.create(**kwargs)
        except (APIError, APIConnectionError, APITimeoutError) as exc:
            error = LLMError(f"LLM API request failed: {exc}")
            error.transient = _is_transient_api_error(exc)  # type: ignore[attr-defined]
            raise error from exc

        if stream:
            return _parse_stream(response, on_stream_chunk=on_stream_chunk)
        return _parse_completion(response)


def _is_transient_api_error(exc: Exception) -> bool:
    if isinstance(exc, (APITimeoutError, APIConnectionError)):
        return True
    if isinstance(exc, APIError):
        code = getattr(exc, "status_code", None)
        return code is None or code >= 500
    return False


def _is_transient(exc: LLMError) -> bool:
    if getattr(exc, "transient", False):
        return True
    message = str(exc).lower()
    if "timeout" in message or "timed out" in message:
        return True
    for code in ("500", "502", "503", "504"):
        if code in message:
            return True
    if "connection" in message:
        return True
    return False


def _merge_stream_field(current: str, delta: str) -> str:
    """Merge streamed tool-call fields across incremental and repeated full chunks."""
    if not delta:
        return current
    if not current:
        return delta
    if delta == current:
        return current
    if delta.startswith(current):
        return delta
    if current.startswith(delta):
        return current
    if current.endswith(delta):
        return current
    return current + delta


def _parse_stream(
    stream: Any,
    on_stream_chunk: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    content_parts: list[str] = []
    tool_calls: dict[int, dict[str, Any]] = {}

    for chunk in stream:
        if isinstance(chunk, str):
            raise LLMError(
                "LLM API returned unexpected text while streaming. "
                f"Response: {chunk[:300]}"
            )
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        if delta.content:
            content_parts.append(delta.content)
            if on_stream_chunk is not None:
                on_stream_chunk(delta.content)
        if delta.tool_calls:
            for tc in delta.tool_calls:
                entry = tool_calls.setdefault(
                    tc.index,
                    {"id": "", "type": "function", "function": {"name": "", "arguments": ""}},
                )
                if tc.id:
                    entry["id"] = tc.id
                if tc.function.name:
                    entry["function"]["name"] = _merge_stream_field(
                        entry["function"]["name"],
                        tc.function.name,
                    )
                if tc.function.arguments:
                    entry["function"]["arguments"] = _merge_stream_field(
                        entry["function"]["arguments"],
                        tc.function.arguments,
                    )

    parsed_tool_calls = [tool_calls[i] for i in sorted(tool_calls)] or None
    return {
        "role": "assistant",
        "content": "".join(content_parts) or None,
        "tool_calls": parsed_tool_calls,
    }


def _parse_completion(response: Any) -> dict[str, Any]:
    if isinstance(response, str):
        if response.lstrip().startswith("data:"):
            raise LLMError(
                "LLM API returned a streaming (SSE) body for a non-streaming request. "
                "Retrying with streaming enabled."
            )
        raise LLMError(
            "LLM API returned a plain string instead of a chat completion. "
            "The provider may not support the tools/function-calling format. "
            f"Response: {response[:300]}"
        )

    choices = getattr(response, "choices", None)
    if not choices:
        raise LLMError(
            "LLM API returned no choices. "
            "Check model name and whether the provider supports chat completions."
        )

    message = choices[0].message
    return {
        "role": "assistant",
        "content": message.content,
        "tool_calls": [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in (message.tool_calls or [])
        ]
        or None,
    }
