from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.core.constants import LevelTypeEnum
from pybot.db.models import UserLevel, Valuation
from pybot.domain.exceptions import UserNotFoundError, ZeroPointsAdjustmentError
from pybot.dto import AdjustUserPointsDTO
from pybot.dto.value_objects import Points
from pybot.services.points import PointsService
from tests.factories import UserSpec, attach_user_level, create_level, create_user


@pytest.mark.asyncio
async def test_change_points_updates_points_level_and_creates_valuation(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(PointsService)

    level_basic = await create_level(db, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    level_next = await create_level(db, name="A1", level_type=LevelTypeEnum.ACADEMIC, required_points=100)

    recipient = await create_user(db, spec=UserSpec(telegram_id=800_001, academic_points=90))
    giver = await create_user(db, spec=UserSpec(telegram_id=800_002))
    await attach_user_level(db, user=recipient, level=level_basic)
    await db.commit()

    dto = AdjustUserPointsDTO(
        recipient_id=recipient.id,
        giver_id=giver.id,
        points=Points(value=20, point_type=LevelTypeEnum.ACADEMIC),
        reason="Great progress",
    )

    # When
    result = await service.change_points(dto)

    # Then
    assert result.academic_points.value == 110

    levels_stmt = select(UserLevel).where(UserLevel.user_id == recipient.id)
    user_levels = (await db.execute(levels_stmt)).scalars().all()
    assert any(link.level_id == level_next.id for link in user_levels)

    valuations_stmt = select(Valuation).where(Valuation.recipient_id == recipient.id)
    valuations = (await db.execute(valuations_stmt)).scalars().all()
    assert len(valuations) == 1
    assert valuations[0].points == 20
    assert valuations[0].giver_id == giver.id


@pytest.mark.asyncio
async def test_change_points_does_not_allow_negative_total_score(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(PointsService)
    level_basic = await create_level(db, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db, name="A1", level_type=LevelTypeEnum.ACADEMIC, required_points=50)

    recipient = await create_user(db, spec=UserSpec(telegram_id=800_003, academic_points=5))
    giver = await create_user(db, spec=UserSpec(telegram_id=800_004))
    await attach_user_level(db, user=recipient, level=level_basic)
    await db.commit()

    dto = AdjustUserPointsDTO(
        recipient_id=recipient.id,
        giver_id=giver.id,
        points=Points(value=-10, point_type=LevelTypeEnum.ACADEMIC),
        reason="Penalty",
    )

    # When
    result = await service.change_points(dto)

    # Then
    assert result.academic_points.value == 0


@pytest.mark.asyncio
async def test_change_points_raises_when_recipient_not_found(
    dishka_request_container,
) -> None:
    # Given
    service = await dishka_request_container.get(PointsService)
    dto = AdjustUserPointsDTO(
        recipient_id=999_001,
        giver_id=999_002,
        points=Points(value=10, point_type=LevelTypeEnum.ACADEMIC),
        reason="No recipient",
    )

    # When / Then
    with pytest.raises(UserNotFoundError):
        await service.change_points(dto)


@pytest.mark.asyncio
async def test_change_points_raises_when_giver_not_found(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(PointsService)

    level_basic = await create_level(db, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db, name="A1", level_type=LevelTypeEnum.ACADEMIC, required_points=100)
    recipient = await create_user(db, spec=UserSpec(telegram_id=800_005, academic_points=10))
    await attach_user_level(db, user=recipient, level=level_basic)
    await db.commit()

    dto = AdjustUserPointsDTO(
        recipient_id=recipient.id,
        giver_id=999_003,
        points=Points(value=10, point_type=LevelTypeEnum.ACADEMIC),
        reason="Missing giver",
    )

    # When / Then
    with pytest.raises(UserNotFoundError):
        await service.change_points(dto)


@pytest.mark.asyncio
async def test_change_points_raises_on_zero_adjustment(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(PointsService)

    level_basic = await create_level(db, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db, name="A1", level_type=LevelTypeEnum.ACADEMIC, required_points=100)
    recipient = await create_user(db, spec=UserSpec(telegram_id=800_006, academic_points=10))
    giver = await create_user(db, spec=UserSpec(telegram_id=800_007))
    await attach_user_level(db, user=recipient, level=level_basic)
    await db.commit()

    dto = AdjustUserPointsDTO(
        recipient_id=recipient.id,
        giver_id=giver.id,
        points=Points(value=0, point_type=LevelTypeEnum.ACADEMIC),
        reason="Zero change",
    )

    # When / Then
    with pytest.raises(ZeroPointsAdjustmentError):
        await service.change_points(dto)
