from collections.abc import Sequence
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository[T]:
    """Базовый репозиторий с CRUD операциями."""

    def __init__(self, db: AsyncSession, model: type[T]) -> None:
        self.db = db
        self.model = model

    async def get_by_id(self, id_: int) -> T | None:
        """Получить сущность по ID."""
        stmt = select(self.model).where(self.model.id == id_)  # ty:ignore[possibly-missing-attribute]
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[T]:
        """Получить все сущности."""
        stmt = select(self.model)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs: dict[Any, Any]) -> T:
        """Создать новую сущность."""
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, id_: int, **kwargs: dict[Any, Any]) -> T | None:
        """Обновить сущность."""
        obj = await self.get_by_id(id_)
        if not obj:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id_: int) -> bool:
        """Удалить сущность."""
        obj = await self.get_by_id(id_)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
