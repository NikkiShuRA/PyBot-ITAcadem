from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.core.constants import LevelTypeEnum, RoleEnum
from pybot.db.models import UserLevel
from pybot.domain.exceptions import InitialLevelsNotFoundError, RoleNotFoundError, UserNotFoundError
from pybot.services.users import UserService
from tests.factories import UserCreateDTOFactory, UserSpec, attach_user_role, create_level, create_role, create_user


@pytest.mark.asyncio
async def test_register_student_success_creates_profile_levels_and_role(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    await create_role(db, name="Student")
    await create_level(db, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db, name="R0", level_type=LevelTypeEnum.REPUTATION, required_points=0)

    dto = UserCreateDTOFactory.build(tg_id=700_001, phone="+79876543210")

    # When
    created = await service.register_student(dto)

    # Then
    assert created.telegram_id == dto.tg_id
    assert created.first_name == dto.first_name

    user_roles = await service.get_user_roles(created.id)
    assert "Student" in user_roles

    levels_stmt = select(UserLevel).where(UserLevel.user_id == created.id)
    user_levels = (await db.execute(levels_stmt)).scalars().all()
    assert len(user_levels) == 2


@pytest.mark.asyncio
async def test_register_student_raises_when_initial_levels_are_missing(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    await create_role(db, name="Student")
    dto = UserCreateDTOFactory.build(tg_id=700_002, phone="+79876543210")

    # When / Then
    with pytest.raises(InitialLevelsNotFoundError):
        await service.register_student(dto)


@pytest.mark.asyncio
async def test_register_student_raises_when_student_role_is_missing(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    await create_level(db, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db, name="R0", level_type=LevelTypeEnum.REPUTATION, required_points=0)
    dto = UserCreateDTOFactory.build(tg_id=700_003, phone="+79876543210")

    # When / Then
    with pytest.raises(RoleNotFoundError):
        await service.register_student(dto)


@pytest.mark.asyncio
async def test_set_user_role_assigns_role_to_existing_user(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user = await create_user(db, spec=UserSpec(telegram_id=700_004))
    await create_role(db, name="Mentor")
    await db.commit()

    # When
    await service.set_user_role(user.id, "Mentor")

    # Then
    roles = await service.get_user_roles(user.id)
    assert "Mentor" in roles


@pytest.mark.asyncio
async def test_set_user_role_raises_for_missing_user(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    await create_role(db, name="Mentor")
    await db.commit()

    # When / Then
    with pytest.raises(UserNotFoundError):
        await service.set_user_role(user_id=999_999, role_name="Mentor")


@pytest.mark.asyncio
async def test_remove_user_role_removes_existing_role_and_returns_dto(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user = await create_user(db, spec=UserSpec(telegram_id=700_005))
    student = await create_role(db, name="Student")
    mentor = await create_role(db, name="Mentor")
    await attach_user_role(db, user=user, role=student)
    await attach_user_role(db, user=user, role=mentor)
    await db.commit()

    # When
    result = await service.remove_user_role(tg_id=user.telegram_id, role_name="Mentor")

    # Then
    assert result is not None
    assert result.id == user.id
    roles = await service.get_user_roles(user.id)
    assert "Mentor" not in roles
    assert "Student" in roles


@pytest.mark.asyncio
async def test_get_user_by_telegram_id_returns_none_for_unknown_user(
    dishka_request_container,
) -> None:
    # Given
    service = await dishka_request_container.get(UserService)

    # When
    result = await service.get_user_by_telegram_id(telegram_id := 123_456_789)

    # Then
    assert result is None, f"Expected no user for telegram id={telegram_id}"


@pytest.mark.asyncio
async def test_add_user_role_raises_when_user_not_found(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    await create_role(db, name="Mentor")
    await db.commit()

    # When / Then
    with pytest.raises(UserNotFoundError):
        await service.add_user_role(telegram_id=321_321_321, new_role=RoleEnum.MENTOR)


@pytest.mark.asyncio
async def test_get_user_roles_returns_all_assigned_roles(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user = await create_user(db, spec=UserSpec(telegram_id=700_006))
    role_student = await create_role(db, name="Student")
    role_admin = await create_role(db, name="Admin")
    await attach_user_role(db, user=user, role=role_student)
    await attach_user_role(db, user=user, role=role_admin)
    await db.commit()

    # When
    roles = await service.get_user_roles(user.id)

    # Then
    assert sorted(roles) == ["Admin", "Student"]
