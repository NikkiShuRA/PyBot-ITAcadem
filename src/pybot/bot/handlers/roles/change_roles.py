"""Модуль бота IT Academ."""

import re

from aiogram.filters.command import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from ....core import logger
from ....core.constants import RoleEnum
from ....domain.exceptions import InvalidRoleChangeError, RoleNotFoundError, UserNotFoundError
from ....presentation.texts import (
    ROLE_COMMAND_INVALID_FORMAT,
    ROLE_REASON_QUOTES_REQUIRED,
    ROLE_UNEXPECTED_ERROR,
    TARGET_NOT_FOUND,
    role_add_success,
    role_not_specified,
    role_remove_success,
    role_target_required,
    role_unknown,
    target_selected_mention,
    target_selected_reply,
)
from ....services.user_services import UserRolesService, UserService
from ...filters import check_text_message_correction, create_chat_type_routers

(_, _, change_role_global_router) = create_chat_type_routers("grand_points")


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
            mentioned_id = entity.user.id
            try:
                mentioned_user = await user_service.find_user_by_telegram_id(mentioned_id)
            except UserNotFoundError:
                await message.reply(TARGET_NOT_FOUND)
                return None

            if mentioned_user is None:
                await message.reply(TARGET_NOT_FOUND)
                return None

            await message.reply(target_selected_mention(mentioned_user.first_name))
            return mentioned_user.telegram_id

    return None


async def _extract_role_and_reason(message: Message) -> tuple[RoleEnum | None, str | None]:
    text = check_text_message_correction(message)
    if text is None:
        await message.reply(ROLE_COMMAND_INVALID_FORMAT)
        return None, None

    role_pattern = r"\b(" + "|".join(role.value for role in RoleEnum) + r")\b"
    role_match = re.search(role_pattern, text)
    if not role_match:
        await message.reply(role_not_specified())
        return None, None

    try:
        role = RoleEnum(role_match.group(1))
    except ValueError:
        await message.reply(role_unknown())
        return None, None

    remaining_text = text[role_match.end() :].strip()
    reason = None
    if remaining_text:
        reason_match = re.match(r'^"([^"]*)"', remaining_text)
        if not reason_match:
            reason_match = re.match(r"^'([^']*)'", remaining_text)

        if reason_match:
            reason = reason_match.group(1)
        else:
            await message.reply(ROLE_REASON_QUOTES_REQUIRED)
            return None, None

    return role, reason


@change_role_global_router.message(Command("addrole"), flags={"role": "Admin", "rate_limit": "expensive"})
async def handle_set_role(
    message: Message,
    user_service: FromDishka[UserService],
    user_roles_service: FromDishka[UserRolesService],
    user_id: int,
) -> None:
    """Форматирует текст для ролей."""
    target_id = await _get_target_user_id_from_reply(message)
    if not target_id:
        target_id = await _get_target_user_id_from_mention(message, user_service)

    if not target_id:
        await message.reply(role_target_required("addrole"))
        return

    role, reason = await _extract_role_and_reason(message)
    if role is None:
        return

    try:
        updated_user = await user_roles_service.add_user_role(
            telegram_id=target_id,
            new_role=role,
        )
    except UserNotFoundError:
        await message.reply(TARGET_NOT_FOUND)
    except RoleNotFoundError:
        await message.reply(role_unknown())
    except InvalidRoleChangeError:
        await message.reply(ROLE_UNEXPECTED_ERROR)
    except Exception:
        logger.exception("Unexpected error in handle_set_role")
        await message.reply(ROLE_UNEXPECTED_ERROR)
    else:
        await message.reply(role_add_success(updated_user.first_name, role.value, reason))


@change_role_global_router.message(Command("removerole"), flags={"role": "Admin", "rate_limit": "expensive"})
async def handle_remove_role(
    message: Message,
    user_service: FromDishka[UserService],
    user_roles_service: FromDishka[UserRolesService],
) -> None:
    """Форматирует текст для ролей."""
    target_id = await _get_target_user_id_from_reply(message)
    if not target_id:
        target_id = await _get_target_user_id_from_mention(message, user_service)

    if not target_id:
        await message.reply(role_target_required("removerole"))
        return

    role, reason = await _extract_role_and_reason(message)
    if role is None:
        return

    try:
        updated_user = await user_roles_service.remove_user_role(
            tg_id=target_id,
            role_name=role.value,
        )
    except UserNotFoundError:
        await message.reply(TARGET_NOT_FOUND)
    except RoleNotFoundError:
        await message.reply(role_unknown())
    except InvalidRoleChangeError:
        await message.reply(ROLE_UNEXPECTED_ERROR)
    except Exception:
        logger.exception("Unexpected error in handle_remove_role")
        await message.reply(ROLE_UNEXPECTED_ERROR)
    else:
        await message.reply(role_remove_success(updated_user.first_name, role.value, reason))
