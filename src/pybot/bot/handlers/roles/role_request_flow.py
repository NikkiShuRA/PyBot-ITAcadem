import re
from datetime import datetime

import pendulum
from aiogram import F
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from ....core import logger
from ....core.constants import RequestStatus, RoleEnum
from ....domain.exceptions import (
    RoleAlreadyAssignedError,
    RoleNotFoundError,
    RoleRequestAlreadyExistsError,
    RoleRequestAlreadyProcessedError,
    RoleRequestCooldownError,
    RoleRequestNotFoundError,
    UserNotFoundError,
)
from ....dto import NotifyDTO
from ....services.ports import NotificationPort
from ....services.role_request import RoleRequestService
from ...filters import check_text_message_correction, create_chat_type_routers
from ...keyboards.role_request_keyboard import RoleRequestCB
from ...texts import (
    ROLE_REQUEST_ADMIN_ALREADY_ASSIGNED,
    ROLE_REQUEST_ADMIN_ALREADY_PROCESSED,
    ROLE_REQUEST_ADMIN_APPROVED,
    ROLE_REQUEST_ADMIN_NOT_FOUND,
    ROLE_REQUEST_ADMIN_REJECTED,
    ROLE_REQUEST_ADMIN_ROLE_NOT_FOUND,
    ROLE_REQUEST_ADMIN_USER_NOT_FOUND,
    ROLE_REQUEST_ALREADY_ASSIGNED,
    ROLE_REQUEST_ALREADY_EXISTS,
    ROLE_REQUEST_NOTIFY_ALREADY_ASSIGNED,
    ROLE_REQUEST_NOTIFY_ALREADY_PROCESSED,
    ROLE_REQUEST_NOTIFY_APPROVED,
    ROLE_REQUEST_NOTIFY_NOT_FOUND,
    ROLE_REQUEST_NOTIFY_REJECTED,
    ROLE_REQUEST_NOTIFY_ROLE_NOT_FOUND,
    ROLE_REQUEST_NOTIFY_UNEXPECTED,
    ROLE_REQUEST_NOTIFY_USER_NOT_FOUND,
    ROLE_REQUEST_UNEXPECTED_ERROR,
    ROLE_REQUEST_USAGE,
    role_request_admin_notification_with_status,
    role_request_cooldown_until,
    role_request_created,
)

(role_request_private_router, _, _) = create_chat_type_routers("grand_points")


async def _finalize_role_request_callback(callback_query: CallbackQuery, status_text: str, lock_buttons: bool) -> None:
    if lock_buttons:
        message = callback_query.message
        if isinstance(message, Message):
            try:
                rendered_text = role_request_admin_notification_with_status(
                    message.html_text or message.text,
                    status_text,
                )
                await message.edit_text(rendered_text, parse_mode="HTML", reply_markup=None)
            except Exception:
                logger.exception("Failed to update role-request admin message")
    await callback_query.answer()


async def _extract_role(message: Message) -> RoleEnum | None:
    text = check_text_message_correction(message)
    if text is None:
        await message.reply(ROLE_REQUEST_USAGE)
        return None

    role_pattern = r"\b(" + "|".join(role.value for role in RoleEnum) + r")\b"
    role_match = re.search(role_pattern, text)

    if not role_match:
        await message.reply(ROLE_REQUEST_USAGE)
        return None

    try:
        return RoleEnum(role_match.group(1))
    except ValueError:
        await message.reply(ROLE_REQUEST_USAGE)
        return None


def _format_role_request_available_at(available_at: datetime, requested_at: datetime) -> str:
    request_time = pendulum.instance(requested_at)
    available_time = pendulum.instance(available_at, tz=request_time.timezone)
    human_diff = f"через {request_time.diff(available_time).in_words(locale='ru')}"
    day_difference = (available_time.date() - request_time.date()).days

    if available_time <= request_time.add(days=1) and day_difference in {0, 1}:
        day_label = "сегодня" if day_difference == 0 else "завтра"
        return f"{day_label} в {available_time.format('HH:mm')} ({human_diff})"

    absolute_time = available_time.format("D MMMM YYYY [в] HH:mm", locale="ru")
    return f"{absolute_time} ({human_diff})"


@role_request_private_router.message(Command("role_request"), flags={"role": "Student", "rate_limit": "moderate"})
async def cmd_role_request(
    message: Message,
    role_request_service: FromDishka[RoleRequestService],
    user_id: int,
) -> None:
    role = await _extract_role(message)
    if role is None:
        return

    try:
        await role_request_service.create_role_request(user_id, role.value)
    except UserNotFoundError:
        await message.reply(ROLE_REQUEST_ADMIN_USER_NOT_FOUND)
    except RoleRequestCooldownError as err:
        await message.reply(
            role_request_cooldown_until(_format_role_request_available_at(err.available_at, message.date))
        )
    except RoleNotFoundError:
        await message.reply(ROLE_REQUEST_ADMIN_ROLE_NOT_FOUND)
    except RoleRequestAlreadyExistsError:
        await message.reply(ROLE_REQUEST_ALREADY_EXISTS)
    except RoleAlreadyAssignedError:
        await message.reply(ROLE_REQUEST_ALREADY_ASSIGNED)
    except Exception:
        await message.reply(ROLE_REQUEST_UNEXPECTED_ERROR)
        logger.exception("Unexpected error in cmd_role_request")
    else:
        await message.reply(role_request_created(role.value))


@role_request_private_router.callback_query(
    RoleRequestCB.filter(F.action == RequestStatus.APPROVED), flags={"role": "Admin"}
)
async def accept_role_request(
    callback_query: CallbackQuery,
    callback_data: RoleRequestCB,
    role_request_service: FromDishka[RoleRequestService],
    notification_service: FromDishka[NotificationPort],
) -> None:
    answer_text = ROLE_REQUEST_ADMIN_NOT_FOUND
    lock_buttons = False
    try:
        await role_request_service.change_request_status(callback_data.request_id, RequestStatus.APPROVED)
    except UserNotFoundError:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_USER_NOT_FOUND, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_USER_NOT_FOUND
        lock_buttons = True
    except RoleNotFoundError:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_ROLE_NOT_FOUND, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_ROLE_NOT_FOUND
        lock_buttons = True
    except RoleRequestNotFoundError:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_NOT_FOUND, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_NOT_FOUND
        lock_buttons = True
    except RoleRequestAlreadyProcessedError:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_ALREADY_PROCESSED, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_ALREADY_PROCESSED
        lock_buttons = True
    except RoleAlreadyAssignedError:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_ALREADY_ASSIGNED, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_ALREADY_ASSIGNED
        lock_buttons = True
    except Exception:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_UNEXPECTED, user_id=callback_query.from_user.id)
        )
        logger.exception("Unexpected error in accept_role_request")
    else:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_APPROVED, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_APPROVED
        lock_buttons = True
    finally:
        await _finalize_role_request_callback(callback_query, status_text=answer_text, lock_buttons=lock_buttons)


@role_request_private_router.callback_query(
    RoleRequestCB.filter(F.action == RequestStatus.REJECTED), flags={"role": "Admin"}
)
async def reject_role_request(
    callback_query: CallbackQuery,
    callback_data: RoleRequestCB,
    role_request_service: FromDishka[RoleRequestService],
    notification_service: FromDishka[NotificationPort],
) -> None:
    answer_text = ROLE_REQUEST_ADMIN_NOT_FOUND
    lock_buttons = False
    try:
        await role_request_service.change_request_status(callback_data.request_id, RequestStatus.REJECTED)
    except UserNotFoundError:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_USER_NOT_FOUND, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_USER_NOT_FOUND
        lock_buttons = True
    except RoleNotFoundError:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_ROLE_NOT_FOUND, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_ROLE_NOT_FOUND
        lock_buttons = True
    except RoleRequestNotFoundError:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_NOT_FOUND, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_NOT_FOUND
        lock_buttons = True
    except RoleRequestAlreadyProcessedError:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_ALREADY_PROCESSED, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_ALREADY_PROCESSED
        lock_buttons = True
    except Exception:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_UNEXPECTED, user_id=callback_query.from_user.id)
        )
        logger.exception("Unexpected error in reject_role_request")
    else:
        await notification_service.send_message(
            NotifyDTO(message=ROLE_REQUEST_NOTIFY_REJECTED, user_id=callback_query.from_user.id)
        )
        answer_text = ROLE_REQUEST_ADMIN_REJECTED
        lock_buttons = True
    finally:
        await _finalize_role_request_callback(callback_query, status_text=answer_text, lock_buttons=lock_buttons)
