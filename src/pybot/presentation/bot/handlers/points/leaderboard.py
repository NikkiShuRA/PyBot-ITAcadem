"""Модуль бота IT Academ."""

from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from .....core import logger
from .....core.constants import PointsTypeEnum
from .....services import LeaderboardService
from ....texts import LEADERBOARD_UNEXPECTED_ERROR, render_leaderboard_message
from ...filters import create_chat_type_routers

(_, _, leaderboard_global_router) = create_chat_type_routers("leaderboard")


@leaderboard_global_router.message(Command("leaderboard"), flags={"rate_limit": "moderate"})
async def handle_leaderboard(
    message: Message,
    leaderboard_service: FromDishka[LeaderboardService],
) -> None:
    """Форматирует текст для таблицы лидеров."""
    try:
        period = leaderboard_service.get_previous_calendar_week_period()
        academic_rows = await leaderboard_service.get_previous_calendar_week_leaderboard(
            points_type=PointsTypeEnum.ACADEMIC,
        )
        reputation_rows = await leaderboard_service.get_previous_calendar_week_leaderboard(
            points_type=PointsTypeEnum.REPUTATION,
        )
    except Exception:
        logger.exception("Unexpected error while loading leaderboard")
        await message.answer(LEADERBOARD_UNEXPECTED_ERROR)
        return

    await message.answer(
        render_leaderboard_message(
            academic_rows=academic_rows,
            reputation_rows=reputation_rows,
            period=period,
        ),
        parse_mode="HTML",
    )
