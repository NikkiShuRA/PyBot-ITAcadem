from __future__ import annotations

from datetime import datetime

import pendulum
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.core.constants import PointsTypeEnum
from pybot.services import LeaderboardService
from tests.factories import PointsTransactionSpec, UserSpec, create_points_transaction, create_user


@pytest.mark.asyncio
async def test_get_previous_calendar_week_leaderboard_uses_previous_week_bounds(
    dishka_request_container,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(LeaderboardService)
    first_user = await create_user(db, spec=UserSpec(telegram_id=840_001, first_name="Ivan"))
    second_user = await create_user(db, spec=UserSpec(telegram_id=840_002, first_name="Petr"))
    giver = await create_user(db, spec=UserSpec(telegram_id=840_003, first_name="Admin"))

    monkeypatch.setattr(
        pendulum,
        "now",
        lambda tz=None: pendulum.datetime(2026, 4, 2, 12, 0, 0, tz=tz or "UTC"),
    )

    await create_points_transaction(
        db,
        spec=PointsTransactionSpec(
            recipient=first_user,
            giver=giver,
            amount=4,
            points_type=PointsTypeEnum.ACADEMIC,
            created_at=datetime(2026, 3, 23, 1, 0, 0),
        ),
    )
    await create_points_transaction(
        db,
        spec=PointsTransactionSpec(
            recipient=second_user,
            giver=giver,
            amount=9,
            points_type=PointsTypeEnum.ACADEMIC,
            created_at=datetime(2026, 3, 28, 12, 0, 0),
        ),
    )
    await create_points_transaction(
        db,
        spec=PointsTransactionSpec(
            recipient=second_user,
            giver=giver,
            amount=30,
            points_type=PointsTypeEnum.ACADEMIC,
            created_at=datetime(2026, 3, 30, 1, 0, 0),
        ),
    )
    await db.commit()

    # When
    leaderboard = await service.get_previous_calendar_week_leaderboard(
        points_type=PointsTypeEnum.ACADEMIC,
        limit=10,
    )

    # Then
    assert len(leaderboard) == 2
    assert leaderboard[0].user_id == second_user.id
    assert leaderboard[0].total_points_delta == 9
    assert leaderboard[1].user_id == first_user.id
    assert leaderboard[1].total_points_delta == 4
    assert leaderboard[0].period_start == datetime(2026, 3, 22, 19, 0, 0)
    assert leaderboard[0].period_end == datetime(2026, 3, 29, 19, 0, 0)
