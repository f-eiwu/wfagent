DISPLAY_TRUNCATE = 500


def truncate_summary(text: str, limit: int = DISPLAY_TRUNCATE) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[:limit] + "..."
