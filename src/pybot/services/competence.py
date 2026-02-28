from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from ..dto.competence_dto import (
    CompetenceByIdDTO,
    CompetenceCreateDTO,
    CompetenceIdsDTO,
    CompetenceReadDTO,
    CompetenceUpdateDTO,
)
from ..infrastructure.competence_repository import CompetenceRepository
from ..mappers.competence_mappers import (
    map_orm_competence_to_competence_read_dto,
    map_orm_competencies_to_competence_read_dtos,
)


class CompetenceService:
    def __init__(self, db: AsyncSession, competence_repository: CompetenceRepository) -> None:
        self.db = db
        self.competence_repository = competence_repository

    async def get_all_competencies(self) -> Sequence[CompetenceReadDTO]:
        competencies = await self.competence_repository.get_all(self.db)
        return await map_orm_competencies_to_competence_read_dtos(competencies)

    async def get_competencies(self, dto: CompetenceIdsDTO) -> Sequence[CompetenceReadDTO]:
        competencies = await self.competence_repository.get_by_ids(self.db, dto.competence_ids)
        found_ids = {competence.id for competence in competencies}
        missing_ids = [competence_id for competence_id in dto.competence_ids if competence_id not in found_ids]
        if missing_ids:
            raise ValueError(f"Competence ids not found: {missing_ids}")

        return await map_orm_competencies_to_competence_read_dtos(competencies)

    async def get_competence_by_id(self, dto: CompetenceByIdDTO) -> CompetenceReadDTO:
        competence = await self.competence_repository.get_by_id(self.db, dto.competence_id)
        if competence is None:
            raise ValueError(f"Competence with id={dto.competence_id} not found")

        return await map_orm_competence_to_competence_read_dto(competence)

    async def create_competence(self, dto: CompetenceCreateDTO) -> CompetenceReadDTO:
        existing = await self.competence_repository.get_by_name(self.db, dto.name)
        if existing is not None:
            raise ValueError(f"Competence with name='{dto.name}' already exists")

        created = await self.competence_repository.create(
            self.db,
            name=dto.name,
            description=dto.description,
        )
        await self.db.commit()

        return await map_orm_competence_to_competence_read_dto(created)

    async def update_competence(self, dto: CompetenceUpdateDTO) -> CompetenceReadDTO:
        competence = await self.competence_repository.get_by_id(self.db, dto.competence_id)
        if competence is None:
            raise ValueError(f"Competence with id={dto.competence_id} not found")

        competence.name = dto.name
        competence.description = dto.description
        updated = await self.competence_repository.update(self.db, competence)
        await self.db.commit()

        return await map_orm_competence_to_competence_read_dto(updated)

    async def delete_competence(self, dto: CompetenceByIdDTO) -> None:
        competence = await self.competence_repository.get_by_id(self.db, dto.competence_id)
        if competence is None:
            raise ValueError(f"Competence with id={dto.competence_id} not found")

        await self.competence_repository.delete(self.db, competence)
        await self.db.commit()
