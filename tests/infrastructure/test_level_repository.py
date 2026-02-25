from __future__ import annotations

import pytest

from pybot.core.constants import LevelTypeEnum
from pybot.infrastructure.level_repository import LevelRepository
from tests.factories import create_level


@pytest.mark.asyncio
async def test_get_all_levels_returns_all_rows(db_session) -> None:
    # Given
    repo = LevelRepository()
    await create_level(db_session, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db_session, name="R0", level_type=LevelTypeEnum.REPUTATION, required_points=0)
    await db_session.commit()

    # When
    levels = await repo.get_all_levels(db_session)

    # Then
    assert len(levels) == 2


@pytest.mark.asyncio
async def test_get_all_by_type_filters_levels(db_session) -> None:
    # Given
    repo = LevelRepository()
    await create_level(db_session, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db_session, name="A1", level_type=LevelTypeEnum.ACADEMIC, required_points=100)
    await create_level(db_session, name="R0", level_type=LevelTypeEnum.REPUTATION, required_points=0)
    await db_session.commit()

    # When
    academic_levels = await repo.get_all_by_type(db_session, LevelTypeEnum.ACADEMIC)

    # Then
    assert len(academic_levels) == 2
    assert all(level.level_type == LevelTypeEnum.ACADEMIC for level in academic_levels)


@pytest.mark.asyncio
async def test_get_initial_levels_returns_only_zero_threshold_levels(db_session) -> None:
    # Given
    repo = LevelRepository()
    await create_level(db_session, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db_session, name="A1", level_type=LevelTypeEnum.ACADEMIC, required_points=100)
    await create_level(db_session, name="R0", level_type=LevelTypeEnum.REPUTATION, required_points=0)
    await db_session.commit()

    # When
    initial_levels = await repo.get_initial_levels(db_session)

    # Then
    assert len(initial_levels) == 2
    assert all(level.required_points == 0 for level in initial_levels)
