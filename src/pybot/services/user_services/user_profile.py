from collections.abc import Sequence

from ...core.constants import PointsTypeEnum
from ...domain.exceptions import LevelNotFoundError
from ...dto import CompetenceReadDTO, ProfileViewDTO, UserLevelReadDTO, UserProfileReadDTO, UserReadDTO
from ...dto.value_objects import Points
from ...mappers.level_mappers import map_orm_level_to_level_read_dto
from ..levels import LevelService
from .user_competence import UserCompetenceService
from .user_roles import UserRolesService


class UserProfileService:
    """Сервис для сборки профиля пользователя.

    Объединяет информацию о пользователе, его ролях, компетенциях и уровнях.
    """

    def __init__(
        self,
        level_service: LevelService,
        user_competence_service: UserCompetenceService,
        user_roles_service: UserRolesService,
    ) -> None:
        """Инициализирует сервис профиля пользователя.

        Args:
            level_service: Сервис для работы с уровнями.
            user_competence_service: Сервис для работы с компетенциями пользователя.
            user_roles_service: Сервис для работы с ролями пользователя.
        """
        self.level_service = level_service
        self.user_competence_service = user_competence_service
        self.user_roles_service = user_roles_service

    async def build_profile_view(self, user_read: UserReadDTO) -> ProfileViewDTO:
        """Собирает и возвращает полные данные для отображения профиля пользователя.

        Args:
            user_read: Базовый DTO пользователя.

        Raises:
            LevelNotFoundError: Если текущий уровень пользователя не найден.

        Returns:
            ProfileViewDTO: Полный DTO профиля для отображения (UI-ready).
        """
        user_profile = await self._collect_user_profile(user_read)

        (
            academic_progress,
            academic_level,
            academic_current_points,
            academic_next_points,
        ) = await self._handle_points_data(user_profile, PointsTypeEnum.ACADEMIC)
        (
            reputation_progress,
            reputation_level,
            reputation_current_points,
            reputation_next_points,
        ) = await self._handle_points_data(user_profile, PointsTypeEnum.REPUTATION)

        return ProfileViewDTO(
            user=user_profile.user,
            academic_progress=academic_progress,
            academic_level=academic_level,
            academic_current_points=academic_current_points,
            academic_next_points=academic_next_points,
            reputation_progress=reputation_progress,
            reputation_level=reputation_level,
            reputation_current_points=reputation_current_points,
            reputation_next_points=reputation_next_points,
            roles_data=user_profile.roles,
            competences=user_profile.competences,
        )

    async def _collect_user_profile(self, user_read_dto: UserReadDTO) -> UserProfileReadDTO:
        levels_data: dict[PointsTypeEnum, UserLevelReadDTO] = await self._get_user_level_data(user_read_dto)
        competences_data: Sequence[CompetenceReadDTO] = await self.user_competence_service.find_user_competencies(
            user_read_dto.id
        )
        roles_data = await self.user_roles_service.find_user_roles(user_read_dto.id)
        return UserProfileReadDTO(
            user=user_read_dto,
            competences=competences_data,
            roles=roles_data,
            level_info=levels_data,
        )

    async def _get_user_level_data(self, user_read_dto: UserReadDTO) -> dict[PointsTypeEnum, UserLevelReadDTO]:
        levels_data: dict[PointsTypeEnum, UserLevelReadDTO] = {}
        for level_system in PointsTypeEnum:
            orm_current_level_res = await self.level_service.find_user_current_level(user_read_dto.id, level_system)
            if orm_current_level_res is None:
                raise LevelNotFoundError(user_read_dto.id)

            _, orm_current_level = orm_current_level_res
            dto_current_level = await map_orm_level_to_level_read_dto(orm_current_level)

            orm_next_level = await self.level_service.find_next_level(orm_current_level, level_system)
            if orm_next_level is None:
                dto_next_level = dto_current_level
            else:
                dto_next_level = await map_orm_level_to_level_read_dto(orm_next_level)

            levels_data[level_system] = UserLevelReadDTO(
                current_level=dto_current_level,
                next_level=dto_next_level,
            )

        return levels_data

    async def _handle_points_data(
        self, user_profile_read: UserProfileReadDTO, point_type: PointsTypeEnum
    ) -> tuple[Points, UserLevelReadDTO, Points, Points]:
        current_progress = getattr(
            user_profile_read.user,
            f"{point_type.value}_points",
            Points(value=0, point_type=point_type),
        )
        user_level = user_profile_read.level_info[point_type]
        current_points = current_progress - user_level.current_level.required_points
        next_points = user_level.next_level.required_points - user_level.current_level.required_points

        return current_progress, user_level, current_points, next_points
