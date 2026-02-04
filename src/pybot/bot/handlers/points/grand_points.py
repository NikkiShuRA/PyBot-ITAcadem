import re

from aiogram.filters.command import Command
from aiogram.types import Message
from dishka import FromDishka
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ....core import logger
from ....core.constants import LevelTypeEnum
from ....dto import AdjustUserPointsDTO, UserReadDTO
from ....dto.value_objects import Points
from ....services.points import PointsService
from ....services.users import UserService
from ...filters import check_text_message_correction, create_chat_type_routers
from ...utils import (
    _get_target_user_id_from_mention,
    _get_target_user_id_from_reply,
    _get_target_user_id_from_text,
)

(_, _, grand_points_global_router) = create_chat_type_routers("grand_points")


async def _extract_points_and_reason(
    message: Message,
) -> tuple[int | None, str | None]:
    """
    Извлечь количество баллов и опциональную причину.

    Формат: /command @user 10 "опциональная причина"
    Причина может быть в одинарных или двойных кавычках.
    """
    text = check_text_message_correction(message)
    if text is None:
        await message.reply("Неверный формат сообщения.")
        return None, None

    # 1️⃣ Извлекаем количество баллов
    points_match = re.search(r'(?:^|\s)(-?\d+)(?=\s|$|"|\')', text)
    if not points_match:
        await message.reply("❌ Не указано количество баллов (число).")
        return None, None

    points = int(points_match.group(1))
    points_end_pos = points_match.end()

    # 2️⃣ Проверяем, есть ли текст после баллов
    remaining_text = text[points_end_pos:].strip()
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

    return points, reason


async def _handle_points_command(
    message: Message,
    db: AsyncSession,
    points_type: LevelTypeEnum,
    points_service: PointsService,
    user_service: UserService,
) -> None:
    """Общий обработчик для выдачи баллов"""
    if not check_text_message_correction(message):
        raise ValueError("Отправленное сообщение некорректно")

    if message.from_user is None:
        return

    target_user_id: int | None = (
        await _get_target_user_id_from_reply(message)
        or await _get_target_user_id_from_mention(message, db)
        or await _get_target_user_id_from_text(message, db)
    )

    if target_user_id is None:
        logger.warning(f"Не удалось определить целевого пользователя: {message.text}")
        return

    points, reason = await _extract_points_and_reason(message)
    if points is None:
        return

    try:
        points = Points(value=points, point_type=points_type)
    except ValidationError as e:
        await message.reply(f"❌ {e}")
        return

    recipient_user: UserReadDTO | None = await user_service.get_user_by_telegram_id(target_user_id)
    giver_user: UserReadDTO | None = await user_service.get_user_by_telegram_id(message.from_user.id)

    if recipient_user is None or giver_user is None:
        logger.warning("Не удалось определить пользователей для операции")
        return

    try:
        await points_service.change_points(
            AdjustUserPointsDTO(
                recipient_id=recipient_user.id,
                giver_id=giver_user.id,
                points=points,
                reason=reason,
            ),
        )

        reason_text = f" Причина: {reason}" if reason else ""
        await message.reply(f"✅ Баллы изменены для ID: {target_user_id}, количество: {points}.{reason_text}")
    except Exception:
        logger.exception("Ошибка при изменении баллов")
        await message.reply("❌ Ошибка при изменении баллов")


@grand_points_global_router.message(Command("academic_points"), flags={"role": "Admin"})
async def handle_academic_points(
    message: Message, db: AsyncSession, user_service: FromDishka[UserService], points_service: FromDishka[PointsService]
) -> None:
    await _handle_points_command(message, db, LevelTypeEnum.ACADEMIC, points_service, user_service)


@grand_points_global_router.message(Command("reputation_points"), flags={"role": "Admin"})
async def handle_reputation_points(
    message: Message, db: AsyncSession, user_service: FromDishka[UserService], points_service: FromDishka[PointsService]
) -> None:
    await _handle_points_command(message, db, LevelTypeEnum.REPUTATION, points_service, user_service)
