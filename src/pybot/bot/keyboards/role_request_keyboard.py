from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class RoleRequestCB(CallbackData, prefix="role_req"):
    action: str
    user_id: int
    role_key: str


def get_admin_decision_kb(user_id: int, role: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Одобрить",
        callback_data=RoleRequestCB(action="approve", user_id=user_id, role_key=role),
    )
    builder.button(text="❌ Отклонить", callback_data=RoleRequestCB(action="reject", user_id=user_id, role_key=role))

    builder.adjust(2)
    return builder.as_markup()
