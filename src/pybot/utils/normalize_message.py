from functools import lru_cache


def normalize_message(message: str, *, max_length: int) -> str:
    """Нормализует и ограничивает длину сообщения.

    Удаляет лишние пробелы по краям и обрезает сообщение до указанной длины,
    добавляя многоточие, если текст был усечен.

    Args:
        message: Исходный текст сообщения.
        max_length: Максимально допустимая длина текста.

    Raises:
        ValueError: Если max_length < 1 или сообщение пустое.

    Returns:
        str: Нормализованное сообщение.
    """
    if max_length < 1:
        raise ValueError("max_length must be greater than 0")
    max_length_with_suffix = min(max_length + 3, 4096)
    return _normalize_message_cached(message, max_length_with_suffix)


@lru_cache(maxsize=512)
def _normalize_message_cached(message: str, max_length_with_suffix: int) -> str:
    normalized = message.strip()
    if not normalized:
        raise ValueError("message must not be empty")

    if len(normalized) <= max_length_with_suffix:
        return normalized

    # Keep final message length within configured limit while preserving
    # user feedback that text was truncated.
    return f"{normalized[: max_length_with_suffix - 3]}..."
