import re

from aiogram.filters.command import Command
from aiogram.types import Message
from dishka import FromDishka
from pydantic import ValidationError

from ....core import logger
from ....core.constants import PointsTypeEnum, TaskScheduleKind
from ....domain.exceptions import DomainError, InvalidPointsValueError, UserNotFoundError, ZeroPointsAdjustmentError
from ....dto import AdjustUserPointsDTO, UserReadDTO
from ....dto.value_objects import Points
from ....services.notification_facade import NotificationFacade, NotifyUserDTO
from ....services.points import PointsService
from ....services.user_services import UserService
from ...filters import check_text_message_correction, create_chat_type_routers
from ...texts import (
    POINTS_AMOUNT_REQUIRED,
    POINTS_COMMAND_INVALID_FORMAT,
    POINTS_OPERATION_FAILED,
    POINTS_REASON_QUOTES_REQUIRED,
    POINTS_UNEXPECTED_ERROR,
    TARGET_NOT_FOUND,
    points_change_success,
    points_invalid_value,
    points_notification,
)
from ...utils import _get_target_user_id_from_mention, _get_target_user_id_from_reply, _get_target_user_id_from_text

(_, _, grand_points_global_router) = create_chat_type_routers("grand_points")


def _build_points_notification_message(
    points: Points,
    points_type: PointsTypeEnum,
    giver_user: UserReadDTO,
    reason: str | None,
) -> str:
    return points_notification(points, points_type, giver_user.first_name, reason)


async def _extract_points_and_reason(message: Message) -> tuple[int | None, str | None]:
    text = check_text_message_correction(message)
    if text is None:
        await message.reply(POINTS_COMMAND_INVALID_FORMAT)
        return None, None

    points_match = re.search(r'(?:^|\s)(-?\d+)(?=\s|$|"|\')', text)
    if not points_match:
        await message.reply(POINTS_AMOUNT_REQUIRED)
        return None, None

    points = int(points_match.group(1))
    remaining_text = text[points_match.end() :].strip()
    reason = None

    if remaining_text:
        reason_match = re.match(r'^"([^"]*)"', remaining_text)
        if not reason_match:
            reason_match = re.match(r"^'([^']*)'", remaining_text)

        if reason_match:
            reason = reason_match.group(1)
        else:
            await message.reply(POINTS_REASON_QUOTES_REQUIRED)
            return None, None

    return points, reason


async def _prepare_points_command_context(
    message: Message,
    points_type: PointsTypeEnum,
    user_service: UserService,
) -> tuple[int, Points, str | None, UserReadDTO, UserReadDTO] | None:
    if not check_text_message_correction(message):
        await message.reply(POINTS_COMMAND_INVALID_FORMAT)
        return None

    if message.from_user is None:
        return None

    prepared_context: tuple[int, Points, str | None, UserReadDTO, UserReadDTO] | None = None
    target_user_id: int | None = (
        await _get_target_user_id_from_reply(message)
        or await _get_target_user_id_from_mention(message, user_service)
        or await _get_target_user_id_from_text(message, user_service)
    )
    if target_user_id is not None:
        raw_points, reason = await _extract_points_and_reason(message)
        if raw_points is not None:
            try:
                points = Points(value=raw_points, point_type=points_type)
            except (ValidationError, ValueError):
                await message.reply(points_invalid_value(raw_points))
            else:
                recipient_user = await user_service.find_user_by_telegram_id(target_user_id)
                giver_user = await user_service.find_user_by_telegram_id(message.from_user.id)
                if recipient_user is None or giver_user is None:
                    logger.warning("Failed to resolve giver or recipient for points command")
                else:
                    prepared_context = target_user_id, points, reason, recipient_user, giver_user
    else:
        logger.warning("Failed to resolve target user for points command: {text}", text=message.text)

    return prepared_context


async def _handle_points_command(
    message: Message,
    points_type: PointsTypeEnum,
    points_service: PointsService,
    user_service: UserService,
    notification_facade: NotificationFacade,
) -> None:
    prepared_context = await _prepare_points_command_context(message, points_type, user_service)
    if prepared_context is None:
        return

    target_user_id, points, reason, recipient_user, giver_user = prepared_context

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
        logger.exception("Error while changing points")
        await message.reply(POINTS_OPERATION_FAILED)
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

    await message.reply(points_change_success(target_user_id, points, reason))


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
            PointsTypeEnum.ACADEMIC,
            points_service,
            user_service,
            notification_facade,
        )
    except UserNotFoundError:
        await message.reply(TARGET_NOT_FOUND)
        logger.warning("User not found in academic points command")
    except ZeroPointsAdjustmentError:
        await message.reply(points_invalid_value(0))
    except InvalidPointsValueError as err:
        await message.reply(points_invalid_value(err.details["value"]))
        logger.exception("Invalid points")
    except DomainError:
        await message.reply(POINTS_OPERATION_FAILED)
        logger.error("Domain error in academic points command", exc_info=True)
    except Exception:
        await message.reply(POINTS_UNEXPECTED_ERROR)
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
            PointsTypeEnum.REPUTATION,
            points_service,
            user_service,
            notification_facade,
        )
    except UserNotFoundError:
        await message.reply(TARGET_NOT_FOUND)
        logger.warning("User not found in reputation points command")
    except ZeroPointsAdjustmentError:
        await message.reply(points_invalid_value(0))
    except InvalidPointsValueError as err:
        await message.reply(points_invalid_value(err.details["value"]))
        logger.exception("Invalid points")
    except DomainError:
        await message.reply(POINTS_OPERATION_FAILED)
        logger.exception("Domain error in handle_reputation_points")
    except Exception:
        await message.reply(POINTS_UNEXPECTED_ERROR)
        logger.exception("Unexpected error in handle_reputation_points")
