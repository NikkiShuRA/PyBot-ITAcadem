import re

from aiogram.filters.command import Command
from aiogram.types import Message
from dishka import FromDishka

from ....core import logger
from ....core.constants import RoleEnum
from ....services.broadcast import BroadcastService
from ...filters import check_text_message_correction, create_chat_type_routers

(broadcast_command_private_router, _, _) = create_chat_type_routers("broadcast")


# TODO Выделить в utils
async def _extract_role(message: Message) -> RoleEnum | None:
    """Extract role from command text: /role_request <RoleName>."""
    text = check_text_message_correction(message)
    if text is None:
        await message.reply("Invalid message format.")
        return None

    role_pattern = r"\b(" + "|".join(role.value for role in RoleEnum) + r")\b"
    role_match = re.search(role_pattern, text)

    if not role_match:
        roles_list = ", ".join(role.value for role in RoleEnum)
        logger.info(f"Role is not specified. Available roles: {roles_list}")
        return None

    try:
        return RoleEnum(role_match.group(1))
    except ValueError:
        logger.info("Unknown role.")
        return None


async def _extract_all_ping(message: Message) -> str | None:
    """Extract @all from command text: /role_request @all"""
    text = check_text_message_correction(message)
    if text is None:
        await message.reply("Invalid message format.")
        return None

    all_pattern = r"(?<!\S)@all(?!\S)"
    role_match = re.search(all_pattern, text, flags=re.IGNORECASE)

    if not role_match:
        logger.info("@all is not specified.")
        return None

    return "all"


async def _extract_message_for_broadcast(message: Message) -> str | None:
    """Extract message for broadcast from command text: /broadcast <message>"""
    text = check_text_message_correction(message)
    if text is None:
        await message.reply("Invalid message format.")
        return None

    role_pattern = r"\b(" + "|".join(re.escape(role.value) for role in RoleEnum) + r")\b"
    all_pattern = r"(?<!\S)@all(?!\S)"
    role_match = re.search(f"{role_pattern}|{all_pattern}", text, flags=re.IGNORECASE)
    start_index = role_match.end() if role_match else 0

    message_pattern = r"\s(.*)$"
    message_match = re.search(message_pattern, text[start_index:])

    if not message_match:
        logger.info("Message for broadcast is not specified.")
        return None

    return message_match.group(1)


@broadcast_command_private_router.message(Command("broadcast"), flags={"role": "Admin", "rate_limit": "expensive"})
async def broadcast_command(message: Message, broadcast_service: FromDishka[BroadcastService]) -> None:
    broadcast_message = await _extract_message_for_broadcast(message)
    if broadcast_message is None:
        return

    all_ping = await _extract_all_ping(message)
    if all_ping:
        await broadcast_service.broadcast_for_all(broadcast_message)
        return

    role = await _extract_role(message)
    if role:
        await broadcast_service.broadcast_for_users_with_role(role.value, broadcast_message)
        return
