from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import Competence
from ...db.models.user_module import User
from ...domain.exceptions import CompetenceNotFoundError, UserNotFoundError
from ...dto import CompetenceReadDTO, UserReadDTO
from ...infrastructure.competence_repository import CompetenceRepository
from ...infrastructure.user_repository import UserRepository
from ...mappers.competence_mappers import map_orm_competencies_to_competence_read_dtos
from ...mappers.user_mappers import map_orm_user_to_user_read_dto
from ...utils import normalize_competence_names


class UserCompetenceService:
    """Сервис для управления компетенциями пользователей.

    Обеспечивает бизнес-логику для получения, добавления, обновления
    и удаления компетенций у конкретных пользователей.
    """

    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        competence_repository: CompetenceRepository,
    ) -> None:
        """Инициализирует сервис компетенций пользователя.

        Args:
            db: Асинхронная сессия базы данных.
            user_repository: Репозиторий пользователей.
            competence_repository: Репозиторий компетенций.
        """
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.competence_repository: CompetenceRepository = competence_repository

    async def find_user_competencies(self, user_id: int) -> Sequence[CompetenceReadDTO]:
        """Возвращает список всех компетенций пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Sequence[CompetenceReadDTO]: Список DTO компетенций.
        """
        competencies = await self.user_repository.find_all_user_competencies(self.db, user_id)
        return await map_orm_competencies_to_competence_read_dtos(competencies)

    async def get_users_with_competence_id(self, competence_id: int) -> Sequence[UserReadDTO]:
        """Возвращает список пользователей, обладающих указанной компетенцией.

        Args:
            competence_id: Идентификатор компетенции.

        Returns:
            Sequence[UserReadDTO]: Список DTO пользователей.
        """
        users = await self.user_repository.get_all_users_with_competence_id(self.db, competence_id)
        return [await map_orm_user_to_user_read_dto(user) for user in users]

    async def add_user_competencies_by_names(self, user_id: int, competence_names: Sequence[str]) -> UserReadDTO:
        """Добавляет пользователю компетенции по их названиям.

        Args:
            user_id: Идентификатор пользователя.
            competence_names: Список названий компетенций для добавления.

        Raises:
            UserNotFoundError: Если пользователь не найден.
            CompetenceNotFoundError: Если одна или несколько компетенций не найдены.

        Returns:
            UserReadDTO: Обновленный DTO пользователя.
        """
        user = await self._get_user(user_id)
        normalized_names = normalize_competence_names(competence_names)
        competencies = await self.competence_repository.find_by_names(self.db, normalized_names)
        self._raise_if_missing_names(normalized_names, competencies)

        user.add_competencies(competencies)
        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def remove_user_competencies_by_names(self, user_id: int, competence_names: Sequence[str]) -> UserReadDTO:
        """Удаляет у пользователя компетенции по их названиям.

        Args:
            user_id: Идентификатор пользователя.
            competence_names: Список названий компетенций для удаления.

        Raises:
            UserNotFoundError: Если пользователь не найден.
            CompetenceNotFoundError: Если одна или несколько компетенций не найдены.

        Returns:
            UserReadDTO: Обновленный DTO пользователя.
        """
        user = await self._get_user(user_id)
        normalized_names = normalize_competence_names(competence_names)
        competencies = await self.competence_repository.find_by_names(self.db, normalized_names)
        self._raise_if_missing_names(normalized_names, competencies)

        user.remove_competencies(competencies)
        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def add_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        """Добавляет пользователю компетенции по их идентификаторам.

        Args:
            user_id: Идентификатор пользователя.
            competence_ids: Список идентификаторов компетенций.

        Raises:
            UserNotFoundError: Если пользователь не найден.

        Returns:
            UserReadDTO: Обновленный DTO пользователя.
        """
        user = await self._get_user(user_id)
        normalized_ids = sorted(set(competence_ids))
        competencies = await self.competence_repository.get_by_ids(self.db, normalized_ids)

        if competencies:
            user.add_competencies(competencies)

        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def remove_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        """Удаляет у пользователя компетенции по их идентификаторам.

        Args:
            user_id: Идентификатор пользователя.
            competence_ids: Список идентификаторов компетенций.

        Raises:
            UserNotFoundError: Если пользователь не найден.

        Returns:
            UserReadDTO: Обновленный DTO пользователя.
        """
        user = await self._get_user(user_id)
        normalized_ids = sorted(set(competence_ids))
        competencies = await self.competence_repository.get_by_ids(self.db, normalized_ids)

        if competencies:
            user.remove_competencies(competencies)

        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def update_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        """Полностью обновляет список компетенций пользователя.

        Старые компетенции удаляются, и устанавливаются только те, что переданы в списке.

        Args:
            user_id: Идентификатор пользователя.
            competence_ids: Новый список идентификаторов компетенций.

        Raises:
            UserNotFoundError: Если пользователь не найден.

        Returns:
            UserReadDTO: Обновленный DTO пользователя.
        """
        user = await self._get_user(user_id)
        current_competencies = await self.user_repository.find_all_user_competencies(self.db, user_id)
        user.remove_competencies(current_competencies)

        normalized_ids = sorted(set(competence_ids))
        competencies = await self.competence_repository.get_by_ids(self.db, normalized_ids)
        if competencies:
            user.add_competencies(competencies)

        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def _get_user(self, user_id: int) -> User:
        try:
            return await self.user_repository.get_by_id(self.db, user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id=user_id) from err

    def _raise_if_missing_names(
        self,
        competence_names: Sequence[str],
        competencies: Sequence[Competence],
    ) -> None:
        found_names = {competence.name.strip().lower() for competence in competencies}
        missing_names = [name for name in competence_names if name not in found_names]
        if missing_names:
            raise CompetenceNotFoundError(missing_names=missing_names)
