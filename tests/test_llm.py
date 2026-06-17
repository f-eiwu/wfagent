from unittest.mock import MagicMock, patch

import pytest

from coding_agent.config import Config
from coding_agent.llm import LLMClient, LLMError, _merge_stream_field, _parse_completion, _parse_stream


class _FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class _FakeChoice:
    def __init__(self, message):
        self.message = message


class _FakeResponse:
    def __init__(self, choices):
        self.choices = choices


class TestParseCompletion:
    def test_parses_standard_response(self):
        response = _FakeResponse(
            [_FakeChoice(_FakeMessage(content="hello", tool_calls=None))]
        )
        result = _parse_completion(response)
        assert result["content"] == "hello"
        assert result["tool_calls"] is None

    def test_raises_on_string_response(self):
        with pytest.raises(LLMError, match="plain string"):
            _parse_completion("not a completion object")

    def test_raises_on_empty_choices(self):
        with pytest.raises(LLMError, match="no choices"):
            _parse_completion(_FakeResponse([]))

    def test_raises_on_sse_string(self):
        with pytest.raises(LLMError, match="streaming"):
            _parse_completion('data: {"choices":[]}')


class _FakeDelta:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class _FakeStreamChoice:
    def __init__(self, delta):
        self.delta = delta


class _FakeStreamChunk:
    def __init__(self, delta):
        self.choices = [_FakeStreamChoice(delta)]


class _FakeToolCall:
    def __init__(self, index, *, id=None, name=None, arguments=None):
        self.index = index
        self.id = id
        self.function = MagicMock()
        self.function.name = name
        self.function.arguments = arguments


class TestParseStream:
    def test_accumulates_content(self):
        chunks = [
            _FakeStreamChunk(_FakeDelta(content="Hi")),
            _FakeStreamChunk(_FakeDelta(content=" there")),
        ]
        result = _parse_stream(chunks)
        assert result["content"] == "Hi there"
        assert result["tool_calls"] is None

    def test_stream_callback(self):
        seen: list[str] = []
        chunks = [
            _FakeStreamChunk(_FakeDelta(content="Hi")),
            _FakeStreamChunk(_FakeDelta(content="!")),
        ]
        result = _parse_stream(chunks, on_stream_chunk=seen.append)
        assert result["content"] == "Hi!"
        assert seen == ["Hi", "!"]

    def test_accumulates_incremental_tool_call_fields(self):
        chunks = [
            _FakeStreamChunk(
                _FakeDelta(
                    tool_calls=[_FakeToolCall(0, id="tc1", name="write", arguments='{"pa')]
                )
            ),
            _FakeStreamChunk(
                _FakeDelta(
                    tool_calls=[
                        _FakeToolCall(0, name="_file", arguments='th": "snake.py"}')
                    ]
                )
            ),
        ]
        result = _parse_stream(chunks)
        assert result["tool_calls"] == [
            {
                "id": "tc1",
                "type": "function",
                "function": {
                    "name": "write_file",
                    "arguments": '{"path": "snake.py"}',
                },
            }
        ]

    def test_does_not_repeat_full_tool_call_chunks(self):
        chunks = [
            _FakeStreamChunk(
                _FakeDelta(
                    tool_calls=[
                        _FakeToolCall(
                            0,
                            id="tc1",
                            name="write_file",
                            arguments='{"path": "snake.py"}',
                        )
                    ]
                )
            ),
            _FakeStreamChunk(
                _FakeDelta(
                    tool_calls=[
                        _FakeToolCall(
                            0,
                            name="write_file",
                            arguments='{"path": "snake.py"}',
                        )
                    ]
                )
            ),
        ]
        result = _parse_stream(chunks)
        assert result["tool_calls"][0]["function"]["name"] == "write_file"
        assert result["tool_calls"][0]["function"]["arguments"] == '{"path": "snake.py"}'


class TestMergeStreamField:
    def test_incremental_merge(self):
        assert _merge_stream_field("write", "_file") == "write_file"

    def test_cumulative_merge(self):
        assert _merge_stream_field("wri", "write_file") == "write_file"

    def test_duplicate_full_chunk(self):
        assert _merge_stream_field("write_file", "write_file") == "write_file"


class TestLLMClientRetry:
    def test_retries_transient_error(self, tmp_workdir):
        from openai import APIError

        config = Config(
            api_key="test-key",
            model="gpt-4o-mini",
            base_url="https://api.openai.com/v1",
            max_steps=5,
            working_dir=tmp_workdir,
            request_timeout=30,
        )
        client = LLMClient(config)
        response = _FakeResponse(
            [_FakeChoice(_FakeMessage(content="ok", tool_calls=None))]
        )
        client._client = MagicMock()
        client._client.chat.completions.create.side_effect = [
            APIError("service unavailable", request=MagicMock(), body=None),
            response,
        ]
        with patch("coding_agent.llm.time.sleep"):
            result = client.chat([{"role": "user", "content": "hi"}])
        assert result["content"] == "ok"
        assert client._client.chat.completions.create.call_count == 2
