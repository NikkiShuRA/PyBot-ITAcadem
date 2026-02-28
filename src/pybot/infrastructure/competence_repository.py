from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Competence


class CompetenceRepository:
    """Stateless repository for Competence model operations."""

    async def get_all(self, db: AsyncSession) -> Sequence[Competence]:
        stmt = select(Competence).order_by(Competence.name.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, competence_id: int) -> Competence | None:
        stmt = select(Competence).where(Competence.id == competence_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, db: AsyncSession, competence_ids: Sequence[int]) -> Sequence[Competence]:
        if not competence_ids:
            return []
        stmt = select(Competence).where(Competence.id.in_(competence_ids)).order_by(Competence.name.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_name(self, db: AsyncSession, name: str) -> Competence | None:
        stmt = select(Competence).where(Competence.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_names(self, db: AsyncSession, names: Sequence[str]) -> Sequence[Competence]:
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
        competence = await self.get_by_id(db, competence_id)
        if competence is None:
            return False
        await self.delete(db, competence)
        return True
