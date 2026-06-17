from typing import Literal

from openai import APIError, OpenAI


class ModelsFetchError(Exception):
    """Raised when the provider model list cannot be retrieved."""


def fetch_models(api_key: str, base_url: str) -> list[str]:
    client = OpenAI(api_key=api_key, base_url=base_url)
    try:
        response = client.models.list()
    except APIError as exc:
        raise ModelsFetchError(f"Failed to fetch models: {exc}") from exc

    ids = sorted({model.id for model in response.data if model.id})
    if not ids:
        raise ModelsFetchError("Provider returned an empty model list")
    return ids


def is_supported(model_id: str, available_models: list[str]) -> bool:
    return model_id in available_models


def _highlight_model_line(
    model_id: str,
    current_model: str,
    highlight: Literal["ansi", "rich"],
) -> str:
    if model_id != current_model:
        return model_id
    if highlight == "rich":
        return f"[green]{model_id}[/green]"
    return f"\033[32m{model_id}\033[0m"


def format_models_list(
    available_models: list[str],
    current_model: str,
    *,
    highlight: Literal[False, "ansi", "rich"] = False,
) -> str:
    lines = []
    for model_id in available_models:
        if highlight:
            lines.append(_highlight_model_line(model_id, current_model, highlight))
        else:
            lines.append(model_id)
    if current_model not in available_models:
        note = f"{current_model}  (current, not in provider list)"
        if highlight:
            marked = _highlight_model_line(current_model, current_model, highlight)
            note = f"{marked}  (not in provider list)"
        lines.insert(0, note)
    return "\n".join(lines)
