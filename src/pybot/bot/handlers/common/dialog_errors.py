from aiogram import Dispatcher
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import CallbackQuery, ErrorEvent
from aiogram_dialog.api.exceptions import UnknownIntent

from ....core import logger

STALE_DIALOG_MESSAGE = "Диалог устарел. Нажмите /start и повторите действие."


async def handle_unknown_intent(event: ErrorEvent) -> bool:
    callback: CallbackQuery | None = event.update.callback_query
    if callback is None:
        logger.warning(
            "UnknownIntent occurred outside callback context, re-raising. update_id={update_id}",
            update_id=event.update.update_id,
        )
        raise event.exception

    logger.warning(
        "Handled stale dialog callback. update_id={update_id}, callback_id={callback_id}, from_user={from_user_id}",
        update_id=event.update.update_id,
        callback_id=callback.id,
        from_user_id=callback.from_user.id,
    )

    try:
        await callback.answer(STALE_DIALOG_MESSAGE, show_alert=True)
    except Exception as exc:
        logger.warning("Failed to answer stale callback query: {error_type}", error_type=type(exc).__name__)
    return True


def register_dialog_error_handlers(dp: Dispatcher) -> None:
    dp.errors.register(handle_unknown_intent, ExceptionTypeFilter(UnknownIntent))
