import re
from re import Match

from aiogram.types import Message

from ...dto import UserReadDTO
from ...services.user_services import UserService
from ..filters.message_value_filters import check_text_message_correction
from ..texts import TARGET_REQUIRED, target_selected_mention, target_selected_reply


async def _get_target_user_id_from_reply(message: Message) -> int | None:
    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username
        await message.reply(target_selected_reply(username or str(target_id)))
        return target_id
    return None


async def _get_target_user_id_from_mention(message: Message, user_service: UserService) -> int | None:
    if not message.entities:
        return None

    for entity in message.entities:
        if entity.type == "text_mention" and entity.user is not None:
            awarded_id = entity.user.id
            mentioned_user = await user_service.find_user_by_telegram_id(awarded_id)

            if mentioned_user is not None:
                await message.reply(target_selected_mention(mentioned_user.first_name))
                return mentioned_user.telegram_id

    return None


async def _get_target_user_id_from_text(message: Message, user_service: UserService) -> int | None:
    text: str | None = check_text_message_correction(message)
    if text is None:
        return None

    match: Match[str] | None = re.search(r"\b(\d+)\b", text)
    if not match:
        await message.reply(TARGET_REQUIRED)
        return None

    user_parsed_id = int(match.group(1))
    user_from_id: UserReadDTO | None = await user_service.find_user_by_telegram_id(user_parsed_id)
    if user_from_id is None:
        await message.reply(TARGET_REQUIRED)
        return None

    return user_from_id.telegram_id
