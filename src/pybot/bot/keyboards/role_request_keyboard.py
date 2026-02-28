from __future__ import annotations

from typing import Literal

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ...core.constants import RequestStatus

ButtonStyle = Literal["success", "danger"]


class RoleRequestCB(CallbackData, prefix="role_req"):
    action: RequestStatus
    request_id: int


def _button(
    *,
    text: str,
    callback_data: str,
    style: ButtonStyle,
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_data,
        style=style,
    )


def get_admin_decision_kb(request_id: int) -> InlineKeyboardMarkup:
    approve_callback_data = RoleRequestCB(action=RequestStatus.APPROVED, request_id=request_id).pack()
    reject_callback_data = RoleRequestCB(action=RequestStatus.REJECTED, request_id=request_id).pack()

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _button(
                    text="Одобрить",
                    callback_data=approve_callback_data,
                    style="success",
                ),
                _button(
                    text="Отклонить",
                    callback_data=reject_callback_data,
                    style="danger",
                ),
            ],
        ]
    )
