from aiogram.types import Message

from .text_id_searches import check_text_message_correction


async def _get_role_name_from_message(message: Message) -> str | None:
    """Получить название роли из сообщения."""
    text: str | None = check_text_message_correction(message)
    if text is None:
        return None
    else:
        return text.strip()[-1].capitalize()
