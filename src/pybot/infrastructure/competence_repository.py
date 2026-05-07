from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Competence
from ..domain.exceptions import CompetenceNotFoundError


class CompetenceRepository:
    """Репозиторий для управления операциями с моделью Competence.

    Предоставляет методы для поиска, создания, обновления и удаления компетенций в базе данных.
    Все методы требуют передачи объекта асинхронной сессии SQLAlchemy.
    """

    async def find_all(self, db: AsyncSession) -> Sequence[Competence]:
        """Возвращает все компетенции, отсортированные по имени.

        Args:
            db: Асинхронная сессия базы данных.

        Returns:
            Sequence[Competence]: Список всех найденных компетенций.
        """
        stmt = select(Competence).order_by(Competence.name.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def find_by_id(self, db: AsyncSession, competence_id: int) -> Competence | None:
        """Находит компетенцию по её идентификатору.

        Args:
            db: Асинхронная сессия базы данных.
            competence_id: Уникальный идентификатор компетенции.

        Returns:
            Competence | None: Объект компетенции или None, если компетенция не найдена.
        """
        stmt = select(Competence).where(Competence.id == competence_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_ids(self, db: AsyncSession, competence_ids: Sequence[int]) -> Sequence[Competence]:
        """Находит несколько компетенций по списку их идентификаторов.

        Args:
            db: Асинхронная сессия базы данных.
            competence_ids: Последовательность идентификаторов компетенций.

        Returns:
            Sequence[Competence]: Список найденных компетенций, отсортированный по имени.
        """
        if not competence_ids:
            return []
        stmt = select(Competence).where(Competence.id.in_(competence_ids)).order_by(Competence.name.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_ids(self, db: AsyncSession, competence_ids: Sequence[int]) -> Sequence[Competence]:
        """Получает компетенции по списку ID или вызывает исключение, если какая-то не найдена.

        Args:
            db: Асинхронная сессия базы данных.
            competence_ids: Список идентификаторов компетенций.

        Returns:
            Sequence[Competence]: Список всех запрошенных компетенций.

        Raises:
            CompetenceNotFoundError: Если одна или несколько компетенций не найдены.
        """
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
        """Находит компетенцию по точному совпадению имени.

        Args:
            db: Асинхронная сессия базы данных.
            name: Название компетенции.

        Returns:
            Competence | None: Объект компетенции или None, если не найдена.
        """
        stmt = select(Competence).where(Competence.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_names(self, db: AsyncSession, names: Sequence[str]) -> Sequence[Competence]:
        """Находит несколько компетенций по списку их названий.

        Имена нормализуются (удаляются пробелы, приводится к нижнему регистру).

        Args:
            db: Асинхронная сессия базы данных.
            names: Список названий компетенций.

        Returns:
            Sequence[Competence]: Список найденных компетенций.
        """
        normalized_names = list(dict.fromkeys(name.strip().lower() for name in names if name.strip()))
        if not normalized_names:
            return []

        stmt = (
            select(Competence).where(func.lower(Competence.name).in_(normalized_names)).order_by(Competence.name.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, name: str, description: str | None = None) -> Competence:
        """Создает новую компетенцию.

        Args:
            db: Асинхронная сессия базы данных.
            name: Название компетенции.
            description: Необязательное описание компетенции.

        Returns:
            Competence: Обьект созданной компетенции.
        """
        competence = Competence(name=name, description=description)
        db.add(competence)
        await db.flush()
        return competence

    async def update(self, db: AsyncSession, competence: Competence) -> Competence:
        """Обновляет существующую компетенцию.

        Args:
            db: Асинхронная сессия базы данных.
            competence: Объект компетенции с измененными данными.

        Returns:
            Competence: Обновленный объект компетенции.
        """
        db.add(competence)
        await db.flush()
        return competence

    async def delete(self, db: AsyncSession, competence: Competence) -> None:
        """Удаляет указанную компетенцию.

        Args:
            db: Асинхронная сессия базы данных.
            competence: Объект компетенции для удаления.
        """
        await db.delete(competence)
        await db.flush()

    async def delete_by_id(self, db: AsyncSession, competence_id: int) -> bool:
        """Удаляет компетенцию по её идентификатору.

        Args:
            db: Асинхронная сессия базы данных.
            competence_id: Идентификатор компетенции.

        Returns:
            bool: True, если компетенция была найдена и удалена, иначе False.
        """
        competence = await self.find_by_id(db, competence_id)
        if competence is None:
            return False
        await self.delete(db, competence)
        return True
