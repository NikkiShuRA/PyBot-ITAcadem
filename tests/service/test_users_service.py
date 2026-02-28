from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.core.config import settings
from pybot.core.constants import LevelTypeEnum, RoleEnum
from pybot.db.models import UserLevel
from pybot.domain.exceptions import InitialLevelsNotFoundError, RoleNotFoundError, UserNotFoundError
from pybot.infrastructure.user_repository import UserRepository
from pybot.services.users import UserService
from tests.factories import (
    UserCreateDTOFactory,
    UserSpec,
    attach_user_competence,
    attach_user_role,
    create_competence,
    create_level,
    create_role,
    create_user,
)


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
async def test_register_student_assigns_admin_role_for_configured_telegram_ids(
    dishka_request_container,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    await create_role(db, name="Student")
    await create_role(db, name="Admin")
    await create_level(db, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db, name="R0", level_type=LevelTypeEnum.REPUTATION, required_points=0)
    auto_admin_tg_id = 700_099
    monkeypatch.setattr(settings, "auto_admin_telegram_ids", {auto_admin_tg_id})
    dto = UserCreateDTOFactory.build(tg_id=auto_admin_tg_id, phone="+79876540099")

    # When
    created = await service.register_student(dto)

    # Then
    roles = await service.get_user_roles(created.id)
    assert sorted(roles) == ["Admin", "Student"]


@pytest.mark.asyncio
async def test_register_student_raises_when_admin_role_is_missing_for_configured_auto_admin_id(
    dishka_request_container,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    await create_role(db, name="Student")
    await create_level(db, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db, name="R0", level_type=LevelTypeEnum.REPUTATION, required_points=0)
    auto_admin_tg_id = 700_102
    monkeypatch.setattr(settings, "auto_admin_telegram_ids", {auto_admin_tg_id})
    dto = UserCreateDTOFactory.build(tg_id=auto_admin_tg_id, phone="+79876540102")

    # When / Then
    with pytest.raises(RoleNotFoundError, match="Роль 'Admin'"):
        await service.register_student(dto)


@pytest.mark.asyncio
async def test_register_student_does_not_assign_admin_role_for_non_configured_telegram_ids(
    dishka_request_container,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    await create_role(db, name="Student")
    await create_role(db, name="Admin")
    await create_level(db, name="A0", level_type=LevelTypeEnum.ACADEMIC, required_points=0)
    await create_level(db, name="R0", level_type=LevelTypeEnum.REPUTATION, required_points=0)
    monkeypatch.setattr(settings, "auto_admin_telegram_ids", {700_100})
    dto = UserCreateDTOFactory.build(tg_id=700_101, phone="+79876540101")

    # When
    created = await service.register_student(dto)

    # Then
    roles = await service.get_user_roles(created.id)
    assert roles == ["Student"]


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


@pytest.mark.asyncio
async def test_get_users_with_competence_id_returns_matching_users(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    python_competence = await create_competence(db, name="Python")
    user_one = await create_user(db, spec=UserSpec(telegram_id=700_010))
    user_two = await create_user(db, spec=UserSpec(telegram_id=700_011))
    user_three = await create_user(db, spec=UserSpec(telegram_id=700_012))
    await attach_user_competence(db, user=user_one, competence=python_competence)
    await attach_user_competence(db, user=user_two, competence=python_competence)
    await db.commit()

    # When
    users = await service.get_users_with_competence_id(python_competence.id)

    # Then
    assert {user.telegram_id for user in users} == {user_one.telegram_id, user_two.telegram_id}
    assert user_three.telegram_id not in {user.telegram_id for user in users}


@pytest.mark.asyncio
async def test_add_user_competencies_adds_links_for_user(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user_repository = await dishka_request_container.get(UserRepository)
    user = await create_user(db, spec=UserSpec(telegram_id=700_013))
    python_competence = await create_competence(db, name="Python")
    sql_competence = await create_competence(db, name="SQL")
    await db.commit()

    # When
    await service.add_user_competencies(user.id, [python_competence.id, sql_competence.id])

    # Then
    loaded = await user_repository.get_by_id(db, user.id)
    assert loaded is not None
    assert sorted(link.competence_id for link in loaded.competencies) == [python_competence.id, sql_competence.id]


@pytest.mark.asyncio
async def test_remove_user_competencies_removes_only_requested_links(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user_repository = await dishka_request_container.get(UserRepository)
    user = await create_user(db, spec=UserSpec(telegram_id=700_014))
    python_competence = await create_competence(db, name="Python")
    sql_competence = await create_competence(db, name="SQL")
    await attach_user_competence(db, user=user, competence=python_competence)
    await attach_user_competence(db, user=user, competence=sql_competence)
    await db.commit()

    # When
    await service.remove_user_competencies(user.id, [python_competence.id])

    # Then
    loaded = await user_repository.get_by_id(db, user.id)
    assert loaded is not None
    assert [link.competence_id for link in loaded.competencies] == [sql_competence.id]


@pytest.mark.asyncio
async def test_update_user_competencies_replaces_existing_set(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user_repository = await dishka_request_container.get(UserRepository)
    user = await create_user(db, spec=UserSpec(telegram_id=700_015))
    python_competence = await create_competence(db, name="Python")
    sql_competence = await create_competence(db, name="SQL")
    go_competence = await create_competence(db, name="Go")
    await attach_user_competence(db, user=user, competence=python_competence)
    await db.commit()

    # When
    await service.update_user_competencies(user.id, [sql_competence.id, go_competence.id])

    # Then
    loaded = await user_repository.get_by_id(db, user.id)
    assert loaded is not None
    assert sorted(link.competence_id for link in loaded.competencies) == [sql_competence.id, go_competence.id]


@pytest.mark.asyncio
async def test_add_user_competencies_raises_for_unknown_competence_id(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user = await create_user(db, spec=UserSpec(telegram_id=700_016))
    await db.commit()

    # When / Then
    with pytest.raises(ValueError, match="Competence ids not found"):
        await service.add_user_competencies(user.id, [999_999])


@pytest.mark.asyncio
async def test_get_user_competencies_returns_read_dto_list(dishka_request_container) -> None:
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user = await create_user(db, spec=UserSpec(telegram_id=700_017))
    python_competence = await create_competence(db, name="Python")
    sql_competence = await create_competence(db, name="SQL")
    await attach_user_competence(db, user=user, competence=python_competence)
    await attach_user_competence(db, user=user, competence=sql_competence)
    await db.commit()

    competencies = await service.get_user_competencies(user.id)

    assert [competence.name for competence in competencies] == ["Python", "SQL"]


@pytest.mark.asyncio
async def test_add_user_competencies_by_names_adds_competencies(dishka_request_container) -> None:
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user_repository = await dishka_request_container.get(UserRepository)
    user = await create_user(db, spec=UserSpec(telegram_id=700_018))
    python_competence = await create_competence(db, name="Python")
    sql_competence = await create_competence(db, name="SQL")
    await db.commit()

    await service.add_user_competencies_by_names(user.id, ["python", "SQL"])

    loaded = await user_repository.get_by_id(db, user.id)
    assert loaded is not None
    assert sorted(link.competence_id for link in loaded.competencies) == [python_competence.id, sql_competence.id]


@pytest.mark.asyncio
async def test_remove_user_competencies_by_names_removes_selected_competencies(dishka_request_container) -> None:
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user_repository = await dishka_request_container.get(UserRepository)
    user = await create_user(db, spec=UserSpec(telegram_id=700_019))
    python_competence = await create_competence(db, name="Python")
    sql_competence = await create_competence(db, name="SQL")
    await attach_user_competence(db, user=user, competence=python_competence)
    await attach_user_competence(db, user=user, competence=sql_competence)
    await db.commit()

    await service.remove_user_competencies_by_names(user.id, ["python"])

    loaded = await user_repository.get_by_id(db, user.id)
    assert loaded is not None
    assert [link.competence_id for link in loaded.competencies] == [sql_competence.id]


@pytest.mark.asyncio
async def test_add_user_competencies_by_names_is_atomic_when_unknown_names_present(dishka_request_container) -> None:
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(UserService)
    user_repository = await dishka_request_container.get(UserRepository)
    user = await create_user(db, spec=UserSpec(telegram_id=700_020))
    python_competence = await create_competence(db, name="Python")
    await attach_user_competence(db, user=user, competence=python_competence)
    await create_competence(db, name="SQL")
    await db.commit()

    with pytest.raises(ValueError, match="Competence names not found"):
        await service.add_user_competencies_by_names(user.id, ["Python", "Unknown"])

    loaded = await user_repository.get_by_id(db, user.id)
    assert loaded is not None
    assert [link.competence_id for link in loaded.competencies] == [python_competence.id]
