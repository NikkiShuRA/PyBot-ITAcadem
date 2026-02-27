from __future__ import annotations

from datetime import UTC, datetime

import pytest

from pybot.core.constants import LevelTypeEnum
from pybot.domain.exceptions import UserNotFoundError, UsersNotFoundError
from pybot.infrastructure.user_repository import UserRepository
from tests.factories import (
    attach_user_competence,
    UserSpec,
    create_competence,
    attach_user_level,
    attach_user_role,
    create_level,
    create_role,
    create_user,
)


@pytest.mark.asyncio
async def test_get_by_id_returns_user_with_loaded_relations(db_session) -> None:
    # Given
    repo = UserRepository()
    user = await create_user(db_session, spec=UserSpec(telegram_id=500_001))
    role = await create_role(db_session, name="Student")
    level = await create_level(db_session, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await attach_user_role(db_session, user=user, role=role)
    await attach_user_level(db_session, user=user, level=level)
    await db_session.commit()

    # When
    loaded = await repo.get_by_id(db_session, user.id)

    # Then
    assert loaded is not None
    assert loaded.id == user.id
    assert len(loaded.roles) == 1
    assert len(loaded.user_levels) == 1


@pytest.mark.asyncio
async def test_get_by_id_raises_when_user_missing(db_session) -> None:
    # Given
    repo = UserRepository()

    # When / Then
    with pytest.raises(UserNotFoundError):
        await repo.get_by_id(db_session, 404_404)


@pytest.mark.asyncio
async def test_get_by_telegram_id_returns_user_or_raises(db_session) -> None:
    # Given
    repo = UserRepository()
    user = await create_user(db_session, spec=UserSpec(telegram_id=500_002))
    await db_session.commit()

    # When
    loaded = await repo.get_by_telegram_id(db_session, user.telegram_id)

    # Then
    assert loaded is not None
    assert loaded.id == user.id

    with pytest.raises(UserNotFoundError):
        await repo.get_by_telegram_id(db_session, 999_999_999)


@pytest.mark.asyncio
async def test_has_role_returns_true_and_false(db_session) -> None:
    # Given
    repo = UserRepository()
    user = await create_user(db_session, spec=UserSpec(telegram_id=500_003))
    role_admin = await create_role(db_session, name="Admin")
    await attach_user_role(db_session, user=user, role=role_admin)
    await db_session.commit()

    # When / Then
    assert await repo.has_role(db_session, user.id, "Admin") is True
    assert await repo.has_role(db_session, user.id, "Mentor") is False


@pytest.mark.asyncio
async def test_get_all_users_with_role_filters_and_raises_on_empty(db_session) -> None:
    # Given
    repo = UserRepository()
    user = await create_user(db_session, spec=UserSpec(telegram_id=500_004))
    role_student = await create_role(db_session, name="Student")
    await attach_user_role(db_session, user=user, role=role_student)
    await db_session.commit()

    # When
    students = await repo.get_all_users_with_role(db_session, "Student")

    # Then
    assert len(students) == 1
    assert students[0].id == user.id

    with pytest.raises(UsersNotFoundError):
        await repo.get_all_users_with_role(db_session, "Mentor")


@pytest.mark.asyncio
async def test_get_all_user_competencies_returns_user_competencies(db_session) -> None:
    # Given
    repo = UserRepository()
    user = await create_user(db_session, spec=UserSpec(telegram_id=500_040))
    python_competence = await create_competence(db_session, name="Python")
    sql_competence = await create_competence(db_session, name="SQL")
    await attach_user_competence(db_session, user=user, competence=python_competence)
    await attach_user_competence(db_session, user=user, competence=sql_competence)
    await db_session.commit()

    # When
    competencies = await repo.get_all_user_competencies(db_session, user.id)

    # Then
    assert [competence.name for competence in competencies] == ["Python", "SQL"]


@pytest.mark.asyncio
async def test_get_all_users_with_competence_id_filters_and_raises_on_empty(db_session) -> None:
    # Given
    repo = UserRepository()
    first_user = await create_user(db_session, spec=UserSpec(telegram_id=500_041))
    second_user = await create_user(db_session, spec=UserSpec(telegram_id=500_042))
    python_competence = await create_competence(db_session, name="Python")
    go_competence = await create_competence(db_session, name="Go")
    await attach_user_competence(db_session, user=first_user, competence=python_competence)
    await attach_user_competence(db_session, user=second_user, competence=go_competence)
    await db_session.commit()

    # When
    users = await repo.get_all_users_with_competence_id(db_session, python_competence.id)

    # Then
    assert len(users) == 1
    assert users[0].id == first_user.id

    with pytest.raises(UsersNotFoundError):
        await repo.get_all_users_with_competence_id(db_session, competence_id=999_999)


@pytest.mark.asyncio
async def test_update_user_last_active_sets_value_for_inactive_user(db_session) -> None:
    # Given
    repo = UserRepository()
    user = await create_user(db_session, spec=UserSpec(telegram_id=500_005))
    await db_session.commit()

    # When
    await repo.update_user_last_active(db_session, user.id)
    await db_session.commit()
    await db_session.refresh(user)

    # Then
    assert user.last_active_at is not None


@pytest.mark.asyncio
async def test_update_user_last_active_skips_update_when_recent(db_session) -> None:
    # Given
    repo = UserRepository()
    user = await create_user(db_session, spec=UserSpec(telegram_id=500_006))
    original = datetime.now(UTC).replace(tzinfo=None, microsecond=0)
    user.last_active_at = original
    await db_session.commit()

    # When
    await repo.update_user_last_active(db_session, user.id)
    await db_session.commit()
    await db_session.refresh(user)

    # Then
    assert user.last_active_at == original
