from ..core import settings


def normalize_message(message: str) -> str:
    normalized = message.strip()
    if not normalized:
        raise ValueError("message must not be empty")

    max_length_with_suffix = min(settings.broadcast_max_text_length + 3, 4096)
    if len(normalized) <= max_length_with_suffix:
        return normalized

    # Keep final message length within configured limit while preserving
    # user feedback that text was truncated.
    return f"{normalized[: max_length_with_suffix - 3]}..."
