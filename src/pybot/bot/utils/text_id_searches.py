import re
from re import Match

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ...dto import UserReadDTO
from ...services.users import get_user_by_telegram_id
from ..filters.message_value_filters import check_text_message_correction


async def _get_target_user_id_from_reply(message: Message) -> int | None:
    """Получить ID из reply_to_message"""
    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username
        await message.reply(f"Вы выбрали пользователя (reply) {username or target_id}.")
        return target_id
    return None


async def _get_target_user_id_from_mention(message: Message, db: AsyncSession) -> int | None:
    """Получить ID из упоминаний (@username)"""
    if not message.entities:
        return None

    for entity in message.entities:
        if entity.type == "text_mention" and entity.user is not None:
            awarded_id = entity.user.id
            mentioned_user = await get_user_by_telegram_id(db, awarded_id)

            if mentioned_user is not None:
                await message.reply(f"Вы выбрали пользователя (text_mention) {mentioned_user.first_name}.")
                return mentioned_user.telegram_id

    return None


async def _get_target_user_id_from_text(message: Message, db: AsyncSession) -> int | None:
    """Парсить ID из текста сообщения"""
    text: str | None = check_text_message_correction(message)
    if text is None:
        return None
    else:
        match: Match[str] | None = re.search(r"\b(\d+)\b", text)
    if not match:
        await message.reply(
            "Не удалось определить пользователя. Пожалуйста, ответьте на его сообщение, "
            "упомяните его (@username) или укажите его ID."
        )
        return None

    user_parsed_id: int = int(match.group(1))
    user_from_id: UserReadDTO | None = await get_user_by_telegram_id(db, user_parsed_id)

    if user_from_id is None:
        await message.reply(
            "Не удалось определить пользователя. Пожалуйста, ответьте на его сообщение, "
            "упомяните его (@username) или укажите его ID."
        )
        return None

    return user_from_id.telegram_id
