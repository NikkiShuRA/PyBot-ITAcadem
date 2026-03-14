import textwrap
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from pybot import NotifyDTO

from ...core.constants import LevelTypeEnum
from ...dto import UserLevelReadDTO, UserProfileReadDTO, UserReadDTO
from ...dto.value_objects import Points
from ...mappers.level_mappers import map_orm_level_to_level_read_dto
from ...utils import progress_bar
from ..levels import LevelService
from ..ports import NotificationPort
from ..users import UserService


@dataclass(frozen=True, slots=True)
class ProfileMessagePO:
    user: UserReadDTO
    academic_progress: Points
    academic_level: UserLevelReadDTO
    academic_current_points: Points
    academic_next_points: Points
    reputation_progress: Points
    reputation_level: UserLevelReadDTO
    reputation_current_points: Points
    reputation_next_points: Points


class UserProfileService:
    def __init__(
        self,
        db: AsyncSession,
        user_service: UserService,
        level_service: LevelService,
        notification_port: NotificationPort,
    ) -> None:
        self.db = db
        self.user_service = user_service
        self.level_service = level_service
        self.notification_port = notification_port

    async def _collect_user_profile(self, user_read_dto: UserReadDTO) -> UserProfileReadDTO:
        levels_data: dict[LevelTypeEnum, UserLevelReadDTO] = {}
        for level_system in LevelTypeEnum:
            orm_current_level_res = await self.level_service.find_user_current_level(user_read_dto.id, level_system)
            if orm_current_level_res is None:
                raise ValueError(f"Уровень пользователя (id:{user_read_dto.id}) не был найден")

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

        return UserProfileReadDTO(user=user_read_dto, level_info=levels_data)

    async def _handle_points_data(
        self, user_profile_read: UserProfileReadDTO, point_type: LevelTypeEnum
    ) -> tuple[Points, UserLevelReadDTO, Points, Points]:

        current_progress = getattr(
            user_profile_read.user, f"{point_type.value}_points", Points(value=0, point_type=point_type)
        )
        user_level = user_profile_read.level_info[point_type]
        current_points = current_progress - user_level.current_level.required_points
        next_points = user_level.next_level.required_points - user_level.current_level.required_points

        return current_progress, user_level, current_points, next_points

    async def _create_profile_message(self, user_profile_data: ProfileMessagePO) -> str:
        ms = textwrap.dedent(
            f"""
                👋 Доброго времени суток, {user_profile_data.user.first_name}!

                📚 Академический уровень
                {user_profile_data.academic_level.current_level.name}
                {
                progress_bar(
                    user_profile_data.academic_current_points.value, user_profile_data.academic_next_points.value
                )
            }
                Общий счёт: {user_profile_data.academic_progress}

                🤌 Репутационный уровень
                {user_profile_data.reputation_level.current_level.name}
                {
                progress_bar(
                    user_profile_data.reputation_current_points.value, user_profile_data.reputation_next_points.value
                )
            }
                Общий счёт: {user_profile_data.reputation_progress}

                🔄️ Обновить профиль — /profile
            """
        )

        return ms

    async def manage_profile(self, user_read: UserReadDTO) -> None:
        user_profile = await self._collect_user_profile(user_read)

        (
            academic_progress,
            academic_level,
            academic_current_points,
            academic_next_points,
        ) = await self._handle_points_data(user_profile, LevelTypeEnum.ACADEMIC)
        (
            reputation_progress,
            reputation_level,
            reputation_current_points,
            reputation_next_points,
        ) = await self._handle_points_data(user_profile, LevelTypeEnum.REPUTATION)

        ms = await self._create_profile_message(
            ProfileMessagePO(
                user=user_profile.user,
                academic_progress=academic_progress,
                academic_level=academic_level,
                academic_current_points=academic_current_points,
                academic_next_points=academic_next_points,
                reputation_progress=reputation_progress,
                reputation_level=reputation_level,
                reputation_current_points=reputation_current_points,
                reputation_next_points=reputation_next_points,
            )
        )

        await self.notification_port.send_message(NotifyDTO(message=ms, user_id=user_profile.user.telegram_id))
