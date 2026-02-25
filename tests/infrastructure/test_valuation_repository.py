from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from pybot.core.constants import LevelTypeEnum
from pybot.infrastructure.valuation_repository import ValuationRepository
from tests.factories import UserSpec, ValuationSpec, create_user, create_valuation


@pytest.mark.asyncio
async def test_get_history_by_recipient_filters_sorts_and_limits(db_session) -> None:
    # Given
    repo = ValuationRepository()
    recipient = await create_user(db_session, spec=UserSpec(telegram_id=520_001))
    giver = await create_user(db_session, spec=UserSpec(telegram_id=520_002))
    now = datetime.now()

    await create_valuation(
        db_session,
        spec=ValuationSpec(
            recipient=recipient,
            giver=giver,
            points=5,
            points_type=LevelTypeEnum.ACADEMIC,
            created_at=now - timedelta(minutes=3),
        ),
    )
    latest = await create_valuation(
        db_session,
        spec=ValuationSpec(
            recipient=recipient,
            giver=giver,
            points=8,
            points_type=LevelTypeEnum.ACADEMIC,
            created_at=now - timedelta(minutes=1),
        ),
    )
    await create_valuation(
        db_session,
        spec=ValuationSpec(
            recipient=recipient,
            giver=giver,
            points=9,
            points_type=LevelTypeEnum.REPUTATION,
            created_at=now - timedelta(minutes=2),
        ),
    )
    await db_session.commit()

    # When
    history = await repo.get_history_by_recipient(
        db_session,
        recipient_id=recipient.id,
        points_type=LevelTypeEnum.ACADEMIC,
        limit=1,
    )

    # Then
    assert len(history) == 1
    assert history[0].id == latest.id
    assert history[0].points_type == LevelTypeEnum.ACADEMIC


@pytest.mark.asyncio
async def test_get_history_by_recipient_returns_empty_for_unknown_user(db_session) -> None:
    # Given
    repo = ValuationRepository()

    # When
    history = await repo.get_history_by_recipient(
        db_session,
        recipient_id=999_999,
        points_type=LevelTypeEnum.ACADEMIC,
        limit=10,
    )

    # Then
    assert history == []
