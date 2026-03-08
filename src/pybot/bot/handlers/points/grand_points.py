import re

from aiogram.filters.command import Command
from aiogram.types import Message
from dishka import FromDishka
from pydantic import ValidationError

from ....core import logger
from ....core.constants import LevelTypeEnum, TaskScheduleKind
from ....domain.exceptions import (
    DomainError,
    InvalidPointsValueError,
    UserNotFoundError,
    ZeroPointsAdjustmentError,
)
from ....dto import AdjustUserPointsDTO, UserReadDTO
from ....dto.value_objects import Points
from ....services.notification_facade import NotificationFacade, NotifyUserDTO
from ....services.points import PointsService
from ....services.users import UserService
from ...filters import check_text_message_correction, create_chat_type_routers
from ...utils import (
    _get_target_user_id_from_mention,
    _get_target_user_id_from_reply,
    _get_target_user_id_from_text,
)

(_, _, grand_points_global_router) = create_chat_type_routers("grand_points")


def _format_points_type_label(points_type: LevelTypeEnum) -> str:
    match points_type:
        case LevelTypeEnum.ACADEMIC:
            return "академических"
        case LevelTypeEnum.REPUTATION:
            return "репутационных"
        case _:
            return ""


def _build_points_notification_message(
    points: Points,
    points_type: LevelTypeEnum,
    giver_user: UserReadDTO,
    reason: str | None,
) -> str:
    action = "начислил" if points.is_positive() else "снял"
    points_amount = abs(points.value)
    points_label = _format_points_type_label(points_type)
    reason_text = f"\nПричина: {reason}" if reason else ""

    return f"Пользователь {giver_user.first_name} {action} вам {points_amount} {points_label} баллов.{reason_text}"


async def _extract_points_and_reason(
    message: Message,
) -> tuple[int | None, str | None]:
    """Извлечь количество баллов и опциональную причину."""
    text = check_text_message_correction(message)
    if text is None:
        await message.reply("Неверный формат сообщения.")
        return None, None

    points_match = re.search(r'(?:^|\s)(-?\d+)(?=\s|$|"|\')', text)
    if not points_match:
        await message.reply("Не указано количество баллов (число).")
        return None, None

    points = int(points_match.group(1))
    points_end_pos = points_match.end()
    remaining_text = text[points_end_pos:].strip()
    reason = None

    if remaining_text:
        reason_match = re.match(r'^"([^"]*)"', remaining_text)
        if not reason_match:
            reason_match = re.match(r"^'([^']*)'", remaining_text)

        if reason_match:
            reason = reason_match.group(1)
        else:
            await message.reply("Причина должна быть заключена в кавычки: \"причина\" или 'причина'")
            return None, None

    return points, reason


async def _handle_points_command(
    message: Message,
    points_type: LevelTypeEnum,
    points_service: PointsService,
    user_service: UserService,
    notification_facade: NotificationFacade,
) -> None:
    """Общий обработчик для выдачи и снятия баллов."""
    if not check_text_message_correction(message):
        raise ValueError("Отправленное сообщение некорректно")

    if message.from_user is None:
        return

    target_user_id: int | None = (
        await _get_target_user_id_from_reply(message)
        or await _get_target_user_id_from_mention(message, user_service)
        or await _get_target_user_id_from_text(message, user_service)
    )

    if target_user_id is None:
        logger.warning("Не удалось определить целевого пользователя: {text}", text=message.text)
        return

    raw_points, reason = await _extract_points_and_reason(message)
    if raw_points is None:
        return

    try:
        points = Points(value=raw_points, point_type=points_type)
    except ValidationError as err:
        await message.reply(str(err))
        return

    recipient_user: UserReadDTO | None = await user_service.get_user_by_telegram_id(target_user_id)
    giver_user: UserReadDTO | None = await user_service.get_user_by_telegram_id(message.from_user.id)

    if recipient_user is None or giver_user is None:
        logger.warning("Не удалось определить пользователей для операции с баллами")
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
    except Exception:
        logger.exception("Ошибка при изменении баллов")
        await message.reply("Ошибка при изменении баллов")
        return

    try:
        await notification_facade.notify_user(
            NotifyUserDTO(
                user_id=recipient_user.telegram_id,
                message=_build_points_notification_message(points, points_type, giver_user, reason),
                kind=TaskScheduleKind.IMMEDIATE,
            )
        )
    except Exception:
        logger.exception(
            "Failed to enqueue points notification for telegram_id={telegram_id}",
            telegram_id=recipient_user.telegram_id,
        )

    reason_text = f" Причина: {reason}" if reason else ""
    await message.reply(f"Баллы изменены для ID: {target_user_id}, количество: {points}.{reason_text}")


@grand_points_global_router.message(Command("academic_points"), flags={"role": "Admin", "rate_limit": "expensive"})
async def handle_academic_points(
    message: Message,
    user_service: FromDishka[UserService],
    points_service: FromDishka[PointsService],
    notification_facade: FromDishka[NotificationFacade],
) -> None:
    try:
        await _handle_points_command(
            message,
            LevelTypeEnum.ACADEMIC,
            points_service,
            user_service,
            notification_facade,
        )
    except UserNotFoundError as err:
        await message.reply(err.message)
        logger.warning("User not found: {details}", details=err.details)
    except ZeroPointsAdjustmentError as err:
        await message.reply(err.message)
    except InvalidPointsValueError as err:
        await message.reply(f"Некорректное значение баллов: {err.details['value']}")
        logger.exception("Invalid points")
    except DomainError as err:
        await message.reply(f"Ошибка: {err.message}")
        logger.error("Domain error: {error}", error=err, exc_info=True)
    except Exception:
        await message.reply("Неожиданная ошибка. Попробуйте позже.")
        logger.exception("Unexpected error in handle_academic_points")


@grand_points_global_router.message(Command("reputation_points"), flags={"role": "Admin", "rate_limit": "expensive"})
async def handle_reputation_points(
    message: Message,
    user_service: FromDishka[UserService],
    points_service: FromDishka[PointsService],
    notification_facade: FromDishka[NotificationFacade],
) -> None:
    try:
        await _handle_points_command(
            message,
            LevelTypeEnum.REPUTATION,
            points_service,
            user_service,
            notification_facade,
        )
    except UserNotFoundError as err:
        await message.reply(err.message)
        logger.warning("User not found: {details}", details=err.details)
    except ZeroPointsAdjustmentError as err:
        await message.reply(err.message)
    except InvalidPointsValueError as err:
        await message.reply(f"Некорректное значение баллов: {err.details['value']}")
        logger.exception("Invalid points")
    except DomainError as err:
        await message.reply(f"Ошибка: {err.message}")
        logger.exception("Domain error")
    except Exception:
        await message.reply("Неожиданная ошибка. Попробуйте позже.")
        logger.exception("Unexpected error in handle_reputation_points")
