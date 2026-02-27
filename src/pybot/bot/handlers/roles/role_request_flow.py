import re

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
    RoleRequestNotFoundError,
    RoleRequestRejectedError,
    UserNotFoundError,
)
from ....services.ports import NotificationPort
from ....services.role_request import RoleRequestService
from ...filters import check_text_message_correction, create_chat_type_routers
from ...keyboards.role_request_keyboard import RoleRequestCB

(role_request_private_router, _, _) = create_chat_type_routers("grand_points")


async def _finalize_role_request_callback(callback_query: CallbackQuery, answer_text: str, lock_buttons: bool) -> None:
    if lock_buttons:
        message = callback_query.message
        if isinstance(message, Message):
            try:
                await message.edit_reply_markup(reply_markup=None)
            except Exception:
                logger.exception("Failed to clear role-request inline keyboard")
    await callback_query.answer(answer_text)


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
        await message.reply(f"Role is not specified. Available roles: {roles_list}")
        return None

    try:
        return RoleEnum(role_match.group(1))
    except ValueError:
        await message.reply("Unknown role.")
        return None


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
        await message.reply("User was not found.")
    except RoleRequestRejectedError:
        await message.reply("Your previous request was recently rejected. Please try later.")
    except RoleNotFoundError:
        await message.reply("Role was not found.")
    except RoleRequestAlreadyExistsError:
        await message.reply("You already have a pending request for this role.")
    except RoleAlreadyAssignedError:
        await message.reply("This role is already assigned to you.")
    except Exception:
        await message.reply("Unexpected error. Please try again later.")
        logger.exception("Unexpected error in cmd_role_request")
    else:
        await message.reply(f"Role request for {role.value} was sent.")


@role_request_private_router.callback_query(
    RoleRequestCB.filter(F.action == RequestStatus.APPROVED), flags={"role": "Admin"}
)
async def accept_role_request(
    callback_query: CallbackQuery,
    callback_data: RoleRequestCB,
    role_request_service: FromDishka[RoleRequestService],
    notification_service: FromDishka[NotificationPort],
) -> None:
    answer_text = "Error"
    lock_buttons = False
    try:
        await role_request_service.change_request_status(callback_data.request_id, RequestStatus.APPROVED)
    except UserNotFoundError:
        await notification_service.send_message(callback_query.from_user.id, "User was not found.")
        answer_text = "User not found"
        lock_buttons = True
    except RoleNotFoundError:
        await notification_service.send_message(callback_query.from_user.id, "Role was not found.")
        answer_text = "Role not found"
        lock_buttons = True
    except RoleRequestNotFoundError:
        await notification_service.send_message(callback_query.from_user.id, "Role request was not found.")
        answer_text = "Request not found"
        lock_buttons = True
    except RoleRequestAlreadyProcessedError:
        await notification_service.send_message(callback_query.from_user.id, "Role request has already been processed.")
        answer_text = "Already processed"
        lock_buttons = True
    except RoleAlreadyAssignedError:
        await notification_service.send_message(callback_query.from_user.id, "User already has this role.")
        answer_text = "Already assigned"
        lock_buttons = True
    except Exception:
        await notification_service.send_message(
            callback_query.from_user.id, "Unexpected error. Please try again later."
        )
        logger.exception("Unexpected error in accept_role_request")
    else:
        await notification_service.send_message(callback_query.from_user.id, "Role request approved.")
        answer_text = "Approved"
        lock_buttons = True
    finally:
        await _finalize_role_request_callback(callback_query, answer_text=answer_text, lock_buttons=lock_buttons)


@role_request_private_router.callback_query(
    RoleRequestCB.filter(F.action == RequestStatus.REJECTED), flags={"role": "Admin"}
)
async def reject_role_request(
    callback_query: CallbackQuery,
    callback_data: RoleRequestCB,
    role_request_service: FromDishka[RoleRequestService],
    notification_service: FromDishka[NotificationPort],
) -> None:
    answer_text = "Error"
    lock_buttons = False
    try:
        await role_request_service.change_request_status(callback_data.request_id, RequestStatus.REJECTED)
    except UserNotFoundError:
        await notification_service.send_message(callback_query.from_user.id, "User was not found.")
        answer_text = "User not found"
        lock_buttons = True
    except RoleNotFoundError:
        await notification_service.send_message(callback_query.from_user.id, "Role was not found.")
        answer_text = "Role not found"
        lock_buttons = True
    except RoleRequestNotFoundError:
        await notification_service.send_message(callback_query.from_user.id, "Role request was not found.")
        answer_text = "Request not found"
        lock_buttons = True
    except RoleRequestAlreadyProcessedError:
        await notification_service.send_message(callback_query.from_user.id, "Role request has already been processed.")
        answer_text = "Already processed"
        lock_buttons = True
    except Exception:
        await notification_service.send_message(
            callback_query.from_user.id, "Unexpected error. Please try again later."
        )
        logger.exception("Unexpected error in reject_role_request")
    else:
        await notification_service.send_message(callback_query.from_user.id, "Role request rejected.")
        answer_text = "Rejected"
        lock_buttons = True
    finally:
        await _finalize_role_request_callback(callback_query, answer_text=answer_text, lock_buttons=lock_buttons)
