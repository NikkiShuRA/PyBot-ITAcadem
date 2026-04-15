from __future__ import annotations

from datetime import datetime

import pytest

from pybot.core.constants import PointsTypeEnum
from pybot.infrastructure.points_transaction_repository import PointsTransactionRepository
from tests.factories import PointsTransactionSpec, UserSpec, create_points_transaction, create_user


@pytest.mark.asyncio
async def test_find_top_recipients_for_period_aggregates_filters_and_sorts(db_session) -> None:
    # Given
    repo = PointsTransactionRepository()
    first_user = await create_user(db_session, spec=UserSpec(telegram_id=530_001, first_name="Ivan"))
    second_user = await create_user(db_session, spec=UserSpec(telegram_id=530_002, first_name="Petr"))
    third_user = await create_user(db_session, spec=UserSpec(telegram_id=530_004, first_name="Olga"))
    giver = await create_user(db_session, spec=UserSpec(telegram_id=530_003, first_name="Admin"))
    start_at = datetime(2026, 3, 23, 0, 0, 0)
    end_at = datetime(2026, 3, 30, 0, 0, 0)

    await create_points_transaction(
        db_session,
        spec=PointsTransactionSpec(
            recipient=first_user,
            giver=giver,
            amount=5,
            points_type=PointsTypeEnum.ACADEMIC,
            created_at=datetime(2026, 3, 24, 10, 0, 0),
        ),
    )
    await create_points_transaction(
        db_session,
        spec=PointsTransactionSpec(
            recipient=first_user,
            giver=giver,
            amount=-2,
            points_type=PointsTypeEnum.ACADEMIC,
            created_at=datetime(2026, 3, 25, 10, 0, 0),
        ),
    )
    await create_points_transaction(
        db_session,
        spec=PointsTransactionSpec(
            recipient=third_user,
            giver=giver,
            amount=-11,
            points_type=PointsTypeEnum.ACADEMIC,
            created_at=datetime(2026, 3, 26, 9, 30, 0),
        ),
    )
    await create_points_transaction(
        db_session,
        spec=PointsTransactionSpec(
            recipient=second_user,
            giver=giver,
            amount=7,
            points_type=PointsTypeEnum.ACADEMIC,
            created_at=datetime(2026, 3, 26, 10, 0, 0),
        ),
    )
    await create_points_transaction(
        db_session,
        spec=PointsTransactionSpec(
            recipient=second_user,
            giver=giver,
            amount=100,
            points_type=PointsTypeEnum.REPUTATION,
            created_at=datetime(2026, 3, 26, 11, 0, 0),
        ),
    )
    await create_points_transaction(
        db_session,
        spec=PointsTransactionSpec(
            recipient=first_user,
            giver=giver,
            amount=50,
            points_type=PointsTypeEnum.ACADEMIC,
            created_at=datetime(2026, 3, 30, 0, 0, 0),
        ),
    )
    await db_session.commit()

    # When
    leaderboard = await repo.find_top_recipients_for_period(
        db_session,
        points_type=PointsTypeEnum.ACADEMIC,
        start_at=start_at,
        end_at=end_at,
        limit=10,
    )

    # Then
    assert len(leaderboard) == 2
    assert leaderboard[0].user_id == second_user.id
    assert leaderboard[0].total_points_delta == 7
    assert leaderboard[1].user_id == first_user.id
    assert leaderboard[1].total_points_delta == 5
    assert all(row.user_id != third_user.id for row in leaderboard)
    assert all(row.points_type is PointsTypeEnum.ACADEMIC for row in leaderboard)
    assert all(row.period_start == start_at for row in leaderboard)
    assert all(row.period_end == end_at for row in leaderboard)


@pytest.mark.asyncio
async def test_find_top_recipients_for_period_returns_empty_for_missing_rows(db_session) -> None:
    # Given
    repo = PointsTransactionRepository()

    # When
    leaderboard = await repo.find_top_recipients_for_period(
        db_session,
        points_type=PointsTypeEnum.ACADEMIC,
        start_at=datetime(2026, 3, 23, 0, 0, 0),
        end_at=datetime(2026, 3, 30, 0, 0, 0),
        limit=10,
    )

    # Then
    assert leaderboard == []
