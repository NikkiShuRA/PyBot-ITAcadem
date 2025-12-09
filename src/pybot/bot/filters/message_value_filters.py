from aiogram.types import Message


def check_text_message_correction(message: Message) -> str | None:
    """Returns message.text if valid, None otherwise"""
    if message.text is None or not message.text.strip():
        return None
    return message.text


def validate_points_value(points: int) -> None:
    """Проверяет, что значение баллов соответствует int32."""
    int32_range = (2**31 - 1, -(2**31))

    if not int32_range[1] <= points <= int32_range[0]:
        raise ValueError(f"Баллы {points} должны быть в диапазоне int32")
