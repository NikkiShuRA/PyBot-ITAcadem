from aiogram.types import Message


def check_text_message_correction(message: Message) -> str | None:
    """Returns message.text if valid, None otherwise"""
    if message.text is None or not message.text.strip():
        return None
    return message.text
