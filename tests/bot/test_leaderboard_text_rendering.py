from datetime import UTC, datetime

from pybot.bot.texts import LEADERBOARD_EMPTY, render_leaderboard_message
from pybot.core.constants import PointsTypeEnum
from pybot.dto import WeeklyLeaderboardRowDTO
from pybot.dto.leaderboard_dto import LeaderboardPeriod


def _row(
    *,
    user_id: int,
    telegram_id: int,
    first_name: str,
    last_name: str | None,
    total_points_delta: int,
) -> WeeklyLeaderboardRowDTO:
    return WeeklyLeaderboardRowDTO(
        user_id=user_id,
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        patronymic=None,
        total_points_delta=total_points_delta,
        points_type=PointsTypeEnum.ACADEMIC,
        period_start=datetime(2026, 3, 24, 0, 0, 0, tzinfo=UTC),
        period_end=datetime(2026, 3, 31, 0, 0, 0, tzinfo=UTC),
    )


def test_render_leaderboard_message_formats_sections_places_and_links() -> None:
    academic_rows = [
        _row(user_id=1, telegram_id=101, first_name="Иван", last_name="Петров", total_points_delta=50),
        _row(user_id=2, telegram_id=102, first_name="Петр", last_name="Сидоров", total_points_delta=40),
        _row(user_id=3, telegram_id=103, first_name="Анна", last_name="Иванова", total_points_delta=30),
        _row(user_id=4, telegram_id=104, first_name="Олег", last_name="Смирнов", total_points_delta=20),
    ]
    reputation_rows = [
        _row(user_id=5, telegram_id=105, first_name="Елена", last_name="Кузнецова", total_points_delta=15),
    ]

    rendered = render_leaderboard_message(
        academic_rows=academic_rows,
        reputation_rows=reputation_rows,
    )

    assert "<b>Лидерборд за прошлую неделю</b>" in rendered
    assert "24.03.2026 - 30.03.2026" in rendered
    assert "<b>Академические баллы</b>" in rendered
    assert "<b>Репутационные баллы</b>" in rendered
    assert "🥇 <a href='tg://user?id=101'>Иван Петров</a> - <b>50</b>" in rendered
    assert "🥈 <a href='tg://user?id=102'>Петр Сидоров</a> - <b>40</b>" in rendered
    assert "🥉 <a href='tg://user?id=103'>Анна Иванова</a> - <b>30</b>" in rendered
    assert "4. <a href='tg://user?id=104'>Олег Смирнов</a> - <b>20</b>" in rendered
    assert "<a href='tg://user?id=105'>Елена Кузнецова</a> - <b>15</b>" in rendered


def test_render_leaderboard_message_keeps_empty_state_per_section() -> None:
    rendered = render_leaderboard_message(
        academic_rows=[],
        reputation_rows=[],
    )

    assert "<b>Академические баллы</b>" in rendered
    assert "<b>Репутационные баллы</b>" in rendered
    assert rendered.count(LEADERBOARD_EMPTY) == 2


def test_render_leaderboard_message_shows_period_for_empty_sections_when_period_provided() -> None:
    rendered = render_leaderboard_message(
        academic_rows=[],
        reputation_rows=[],
        period=LeaderboardPeriod(
            start=datetime(2026, 3, 24, 0, 0, 0, tzinfo=UTC),
            end=datetime(2026, 3, 31, 0, 0, 0, tzinfo=UTC),
        ),
    )

    assert "24.03.2026 - 30.03.2026" in rendered
    assert rendered.count(LEADERBOARD_EMPTY) == 2
