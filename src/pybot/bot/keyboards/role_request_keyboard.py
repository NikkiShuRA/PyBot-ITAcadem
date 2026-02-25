from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...core.constants import RequestStatus


class RoleRequestCB(CallbackData, prefix="role_req"):
    action: RequestStatus
    request_id: int


def get_admin_decision_kb(request_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Одобрить",
        callback_data=RoleRequestCB(action=RequestStatus.APPROVED, request_id=request_id),
    )
    builder.button(
        text="❌ Отклонить", callback_data=RoleRequestCB(action=RequestStatus.REJECTED, request_id=request_id)
    )

    builder.adjust(2)
    return builder.as_markup()
