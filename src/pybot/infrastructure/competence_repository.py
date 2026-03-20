from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Competence
from ..domain.exceptions import CompetenceNotFoundError


class CompetenceRepository:
    """Stateless repository for Competence model operations."""

    async def find_all(self, db: AsyncSession) -> Sequence[Competence]:
        stmt = select(Competence).order_by(Competence.name.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def find_by_id(self, db: AsyncSession, competence_id: int) -> Competence | None:
        stmt = select(Competence).where(Competence.id == competence_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_ids(self, db: AsyncSession, competence_ids: Sequence[int]) -> Sequence[Competence]:
        if not competence_ids:
            return []
        stmt = select(Competence).where(Competence.id.in_(competence_ids)).order_by(Competence.name.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_ids(self, db: AsyncSession, competence_ids: Sequence[int]) -> Sequence[Competence]:
        normalized_ids = list(dict.fromkeys(competence_ids))
        if not normalized_ids:
            return []

        competencies = await self.find_by_ids(db, normalized_ids)
        found_ids = {competence.id for competence in competencies}
        missing_ids = [competence_id for competence_id in normalized_ids if competence_id not in found_ids]
        if missing_ids:
            raise CompetenceNotFoundError(missing_ids=missing_ids)

        return competencies

    async def find_by_name(self, db: AsyncSession, name: str) -> Competence | None:
        stmt = select(Competence).where(Competence.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_names(self, db: AsyncSession, names: Sequence[str]) -> Sequence[Competence]:
        normalized_names = list(dict.fromkeys(name.strip().lower() for name in names if name.strip()))
        if not normalized_names:
            return []

        stmt = (
            select(Competence).where(func.lower(Competence.name).in_(normalized_names)).order_by(Competence.name.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, name: str, description: str | None = None) -> Competence:
        competence = Competence(name=name, description=description)
        db.add(competence)
        await db.flush()
        return competence

    async def update(self, db: AsyncSession, competence: Competence) -> Competence:
        db.add(competence)
        await db.flush()
        return competence

    async def delete(self, db: AsyncSession, competence: Competence) -> None:
        await db.delete(competence)
        await db.flush()

    async def delete_by_id(self, db: AsyncSession, competence_id: int) -> bool:
        competence = await self.find_by_id(db, competence_id)
        if competence is None:
            return False
        await self.delete(db, competence)
        return True
