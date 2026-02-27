import re

from aiogram.filters.command import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from ....core import logger
from ....core.constants import RoleEnum
from ....domain.exceptions import (
    InvalidRoleChangeError,
    RoleNotFoundError,
    UserNotFoundError,
)
from ....services.users import UserService
from ...filters import check_text_message_correction, create_chat_type_routers

(_, _, change_role_global_router) = create_chat_type_routers("grand_points")


async def _get_target_user_id_from_reply(message: Message) -> int | None:
    """Получить ID из reply_to_message"""
    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username
        await message.reply(f"✅ Вы выбрали пользователя (reply) {username or target_id}.")
        return target_id
    return None


async def _get_target_user_id_from_mention(
    message: Message,
    user_service: UserService,
) -> int | None:
    """Получить ID из упоминаний (@username)"""
    if not message.entities:
        return None

    for entity in message.entities:
        if entity.type == "text_mention" and entity.user is not None:
            awarded_id = entity.user.id
            try:
                mentioned_user = await user_service.get_user_by_telegram_id(awarded_id)
                if mentioned_user is None:
                    await message.reply("❌ Пользователь не найден в системе.")
                    return None
                await message.reply(f"✅ Вы выбрали пользователя (mention) {mentioned_user.first_name}.")
            except UserNotFoundError:
                await message.reply("❌ Пользователь не найден в системе.")
                return None
            else:
                return mentioned_user.telegram_id if mentioned_user is not None else None

    return None


async def _extract_role_and_reason(
    message: Message,
) -> tuple[RoleEnum | None, str | None]:
    """
    Извлечь роль и опциональную причину.

    Формат: /command @user Student "опциональная причина"
    Роли: Student, Mentor, Admin
    Причина может быть в одинарных или двойных кавычках.
    """
    text = check_text_message_correction(message)
    if text is None:
        await message.reply("❌ Неверный формат сообщения.")
        return None, None

    # 1️⃣ Ищем роль (Student, Mentor, Admin)
    role_pattern = r"\b(" + "|".join(role.value for role in RoleEnum) + r")\b"
    role_match = re.search(role_pattern, text)

    if not role_match:
        roles_list = ", ".join(role.value for role in RoleEnum)
        await message.reply(f"❌ Не указана роль. Доступные: {roles_list}")
        return None, None

    try:
        role = RoleEnum(role_match.group(1))
    except ValueError:
        await message.reply("❌ Неизвестная роль.")
        return None, None

    role_end_pos = role_match.end()

    # 2️⃣ Проверяем, есть ли текст после роли
    remaining_text = text[role_end_pos:].strip()
    reason = None

    if remaining_text:
        # Ищем строку в двойных кавычках: "причина"
        reason_match = re.match(r'^"([^"]*)"', remaining_text)

        # Если не нашли двойные, ищем одинарные: 'причина'
        if not reason_match:
            reason_match = re.match(r"^'([^']*)'", remaining_text)

        if reason_match:
            reason = reason_match.group(1)
        else:
            await message.reply("⚠️ Причина должна быть заключена в кавычки: \"причина\" или 'причина'")
            return None, None

    return role, reason


@change_role_global_router.message(Command("addrole"), flags={"role": "Admin", "rate_limit": "expensive"})
async def handle_set_role(
    message: Message,
    user_service: FromDishka[UserService],
    user_id: int,
) -> None:
    """
    Установить роль пользователю.

    Формат: /addrole @user Student "причина изменения"
    или reply на сообщение: /addrole Student "причина"
    """

    # Шаг 1️⃣: Получаем ID пользователя
    target_id = await _get_target_user_id_from_reply(message)

    if not target_id:
        target_id = await _get_target_user_id_from_mention(message, user_service)

    if not target_id:
        await message.reply(
            '❌ Укажите пользователя через reply или @mention\nФормат: /setrole @user Student "причина"'
        )
        return

    # Шаг 2️⃣: Извлекаем роль и причину
    role, reason = await _extract_role_and_reason(message)

    if role is None:
        return  # Ошибка уже отправлена в _extract_role_and_reason

    # Шаг 3️⃣: Вызываем сервис для изменения роли
    try:
        updated_user = await user_service.add_user_role(
            telegram_id=target_id,
            new_role=role,
        )

        await message.reply(
            f"✅ Роль пользователя {updated_user.first_name} "
            f"успешно изменена на {role.value}\n"
            f"📝 Причина: {reason or 'не указана'}"
        )

    except UserNotFoundError as e:
        await message.reply(f"❌ {e.message}")
    except RoleNotFoundError as e:
        await message.reply(f"❌ {e.message}")
    except InvalidRoleChangeError as e:
        await message.reply(f"⚠️ {e.message}")
    except Exception:
        logger.exception("Unexpected error in handle_set_role")
        await message.reply("❌ Неожиданная ошибка при изменении роли")


@change_role_global_router.message(Command("removerole"), flags={"role": "Admin", "rate_limit": "expensive"})
async def handle_remove_role(
    message: Message,
    user_service: FromDishka[UserService],
) -> None:
    target_id = await _get_target_user_id_from_reply(message)

    if not target_id:
        target_id = await _get_target_user_id_from_mention(message, user_service)

    if not target_id:
        await message.reply(
            '❌ Укажите пользователя через reply или @mention\nФормат: /setrole @user Student "причина"'
        )
        return

    # Шаг 2️⃣: Извлекаем роль и причину
    role, reason = await _extract_role_and_reason(message)

    if role is None:
        return  # Ошибка уже отправлена в _extract_role_and_reason

    # Шаг 3️⃣: Вызываем сервис для изменения роли
    try:
        updated_user = await user_service.remove_user_role(
            tg_id=target_id,
            role_name=role.value,
        )

        if not updated_user:
            await message.reply(f"❌ Пользователь {target_id} не имеет роли {role.value}")
            return

        await message.reply(
            f"✅ Роль {role.value} пользователя {updated_user.first_name} "
            f"успешно удалена\n"
            f"📝 Причина: {reason or 'не указана'}"
        )

    except UserNotFoundError as e:
        await message.reply(f"❌ {e.message}")
    except RoleNotFoundError as e:
        await message.reply(f"❌ {e.message}")
    except InvalidRoleChangeError as e:
        await message.reply(f"⚠️ {e.message}")
    except Exception:
        logger.exception("Unexpected error in handle_set_role")
        await message.reply("❌ Неожиданная ошибка при изменении роли")
