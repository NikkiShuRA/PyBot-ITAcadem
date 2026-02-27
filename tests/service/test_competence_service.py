from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.dto import CompetenceByIdDTO, CompetenceCreateDTO, CompetenceIdsDTO, CompetenceUpdateDTO
from pybot.infrastructure.competence_repository import CompetenceRepository
from pybot.services.competence import CompetenceService
from tests.factories import create_competence


@pytest.mark.asyncio
async def test_get_all_competencies_returns_all_sorted(dishka_request_container) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(CompetenceService)
    await create_competence(db, name="SQL")
    await create_competence(db, name="Python")
    await db.commit()

    # When
    competencies = await service.get_all_competencies()

    # Then
    assert [competence.name for competence in competencies] == ["Python", "SQL"]


@pytest.mark.asyncio
async def test_get_competence_by_id_returns_competence(dishka_request_container) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(CompetenceService)
    competence = await create_competence(db, name="Python", description="Backend")
    await db.commit()

    # When
    result = await service.get_competence_by_id(CompetenceByIdDTO(competence_id=competence.id))

    # Then
    assert result.id == competence.id
    assert result.name == "Python"
    assert result.description == "Backend"


@pytest.mark.asyncio
async def test_get_competence_by_id_raises_for_missing_competence(dishka_request_container) -> None:
    # Given
    service = await dishka_request_container.get(CompetenceService)

    # When / Then
    with pytest.raises(ValueError, match="not found"):
        await service.get_competence_by_id(CompetenceByIdDTO(competence_id=999_999))


@pytest.mark.asyncio
async def test_get_competencies_returns_requested_ids(dishka_request_container) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(CompetenceService)
    python = await create_competence(db, name="Python")
    sql = await create_competence(db, name="SQL")
    await db.commit()

    # When
    result = await service.get_competencies(CompetenceIdsDTO(competence_ids=[sql.id, python.id]))

    # Then
    assert [competence.id for competence in result] == [python.id, sql.id]


@pytest.mark.asyncio
async def test_get_competencies_raises_for_missing_ids(dishka_request_container) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(CompetenceService)
    python = await create_competence(db, name="Python")
    await db.commit()

    # When / Then
    with pytest.raises(ValueError, match="not found"):
        await service.get_competencies(CompetenceIdsDTO(competence_ids=[python.id, 999_999]))


@pytest.mark.asyncio
async def test_update_competence_updates_model_and_commits(dishka_request_container) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(CompetenceService)
    repository = await dishka_request_container.get(CompetenceRepository)
    competence = await create_competence(db, name="Python", description="Old")
    await db.commit()

    # When
    updated = await service.update_competence(
        CompetenceUpdateDTO(competence_id=competence.id, name="Python Advanced", description="New")
    )

    # Then
    assert updated.name == "Python Advanced"
    assert updated.description == "New"
    persisted = await repository.get_by_id(db, competence.id)
    assert persisted is not None
    assert persisted.name == "Python Advanced"
    assert persisted.description == "New"


@pytest.mark.asyncio
async def test_create_competence_creates_new_competence(dishka_request_container) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(CompetenceService)
    repository = await dishka_request_container.get(CompetenceRepository)

    # When
    created = await service.create_competence(CompetenceCreateDTO(name="Go", description="Backend language"))

    # Then
    assert created.name == "Go"
    assert created.description == "Backend language"
    persisted = await repository.get_by_id(db, created.id)
    assert persisted is not None
    assert persisted.name == "Go"


@pytest.mark.asyncio
async def test_create_competence_raises_for_duplicate_name(dishka_request_container) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(CompetenceService)
    await create_competence(db, name="Go")
    await db.commit()

    # When / Then
    with pytest.raises(ValueError, match="already exists"):
        await service.create_competence(CompetenceCreateDTO(name="Go"))


@pytest.mark.asyncio
async def test_delete_competence_removes_entity(dishka_request_container) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(CompetenceService)
    repository = await dishka_request_container.get(CompetenceRepository)
    competence = await create_competence(db, name="Docker")
    await db.commit()

    # When
    await service.delete_competence(CompetenceByIdDTO(competence_id=competence.id))

    # Then
    deleted = await repository.get_by_id(db, competence.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_competence_raises_for_missing_competence(dishka_request_container) -> None:
    # Given
    service = await dishka_request_container.get(CompetenceService)

    # When / Then
    with pytest.raises(ValueError, match="not found"):
        await service.delete_competence(CompetenceByIdDTO(competence_id=999_999))
