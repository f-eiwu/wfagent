from unittest.mock import MagicMock, patch

import pytest

from coding_agent.models import (
    ModelsFetchError,
    fetch_models,
    format_models_list,
    is_supported,
)


def _mock_models_response(*ids: str) -> MagicMock:
    response = MagicMock()
    response.data = [MagicMock(id=model_id) for model_id in ids]
    return response


class TestModelCatalog:
    @patch("coding_agent.models.OpenAI")
    def test_fetch_models_returns_sorted_ids(self, mock_openai):
        mock_openai.return_value.models.list.return_value = _mock_models_response(
            "gpt-4o",
            "gpt-4o-mini",
        )

        models = fetch_models("test-key", "https://example.com/v1")

        assert models == ["gpt-4o", "gpt-4o-mini"]
        mock_openai.assert_called_once_with(
            api_key="test-key",
            base_url="https://example.com/v1",
        )

    @patch("coding_agent.models.OpenAI")
    def test_fetch_models_empty_list_raises(self, mock_openai):
        mock_openai.return_value.models.list.return_value = _mock_models_response()

        with pytest.raises(ModelsFetchError, match="empty model list"):
            fetch_models("test-key", "https://example.com/v1")

    @patch("coding_agent.models.OpenAI")
    def test_fetch_models_api_error_raises(self, mock_openai):
        from openai import APIError

        mock_openai.return_value.models.list.side_effect = APIError(
            "bad request",
            request=MagicMock(),
            body=None,
        )

        with pytest.raises(ModelsFetchError, match="Failed to fetch models"):
            fetch_models("test-key", "https://example.com/v1")

    def test_is_supported(self):
        models = ["gpt-4o-mini", "gpt-4o"]
        assert is_supported("gpt-4o-mini", models) is True
        assert is_supported("unknown/model", models) is False

    def test_format_models_list_marks_current(self):
        output = format_models_list(
            ["gpt-4o-mini", "gpt-4o"],
            "gpt-4o",
        )
        assert output.splitlines() == [
            "gpt-4o-mini",
            "gpt-4o",
        ]

    def test_format_models_list_rich_highlight(self):
        output = format_models_list(
            ["gpt-4o-mini", "gpt-4o"],
            "gpt-4o",
            highlight="rich",
        )
        assert output.splitlines() == [
            "gpt-4o-mini",
            "[green]gpt-4o[/green]",
        ]

    def test_format_models_list_ansi_highlight(self):
        output = format_models_list(
            ["gpt-4o-mini"],
            "gpt-4o-mini",
            highlight="ansi",
        )
        assert "\033[32m" in output
        assert "gpt-4o-mini" in output

    def test_format_models_list_shows_current_not_in_provider_list(self):
        output = format_models_list(["gpt-4o-mini"], "custom/model")
        assert "custom/model" in output
        assert "not in provider list" in output
