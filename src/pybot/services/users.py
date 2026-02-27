from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import LevelTypeEnum, RoleEnum
from ..db.models.user_module import User, UserLevel
from ..domain.exceptions import InitialLevelsNotFoundError, RoleNotFoundError, UserNotFoundError
from ..dto import CompetenceReadDTO, UserCreateDTO, UserLevelReadDTO, UserProfileReadDTO, UserReadDTO
from ..infrastructure.competence_repository import CompetenceRepository
from ..infrastructure.level_repository import LevelRepository
from ..infrastructure.role_repository import RoleRepository
from ..infrastructure.user_repository import UserRepository
from ..mappers.competence_mappers import map_orm_competencies_to_competence_read_dtos
from ..mappers.level_mappers import map_orm_level_to_level_read_dto
from ..mappers.user_mappers import map_orm_user_to_user_read_dto
from .levels import get_all_levels, get_next_level, get_user_current_level


class UserService:
    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        level_repository: LevelRepository,
        role_repository: RoleRepository,
        competence_repository: CompetenceRepository,
    ) -> None:
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.level_repository: LevelRepository = level_repository
        self.role_repository: RoleRepository = role_repository
        self.competence_repository: CompetenceRepository = competence_repository

    @staticmethod
    def _normalize_competence_names(competence_names: Sequence[str]) -> list[str]:
        return list(dict.fromkeys(name.strip().lower() for name in competence_names if name.strip()))

    async def register_student(self, dto: UserCreateDTO) -> UserReadDTO:
        initial_levels = await self.level_repository.get_initial_levels(self.db)

        if not initial_levels:
            raise InitialLevelsNotFoundError()

        student_role = await self.role_repository.get_role_by_name(self.db, "Student")
        if not student_role:
            raise RoleNotFoundError(
                "Р РѕР»СЊ 'Student' РЅРµ РЅР°Р№РґРµРЅР° РІ Р±Р°Р·Рµ РґР°РЅРЅС‹С…. РЎРЅР°С‡Р°Р»Р° СЃРѕР·РґР°Р№С‚Рµ РµС‘!"
            )

        user = await self.user_repository.create_user_profile(self.db, data=dto)

        user.set_initial_levels(initial_levels)
        user.add_role(student_role)
        self.db.add(user)

        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)

    async def get_user(
        self,
        user_id: int,
    ) -> UserReadDTO | None:
        # РџСЂРѕРІРµСЂСЏРµРј, РµСЃС‚СЊ Р»Рё РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ
        user = await self.user_repository.get_by_id(self.db, user_id)

        if user:
            return await map_orm_user_to_user_read_dto(user)

        return None

    async def check_user_role(
        self,
        user_id: int,
        user_role: str,
    ) -> bool:
        """РџСЂРѕРІРµСЂРёС‚СЊ, РёРјРµРµС‚ Р»Рё РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ Р·Р°РґР°РЅРЅСѓСЋ СЂРѕР»СЊ."""
        return await self.user_repository.has_role(self.db, user_id, user_role)

    async def set_user_role(self, user_id: int, role_name: str) -> None:
        """РџСЂРёСЃРІРѕРёС‚СЊ СЂРѕР»СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ"""

        user = await self.user_repository.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id=user_id)

        role = await self.role_repository.get_role_by_name(self.db, role_name)

        if not role:
            raise RoleNotFoundError(f"Role '{role_name}' was not found.")

        user.add_role(role)

        await self.db.commit()

    async def remove_user_role(self, tg_id: int, role_name: str) -> UserReadDTO | None:
        """РЈРґР°Р»РёС‚СЊ СЂРѕР»СЊ Сѓ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ"""

        # Get user with preloaded roles.
        user = await self.user_repository.get_by_telegram_id(self.db, tg_id)
        if not user:
            raise UserNotFoundError(user_id=tg_id)

        role = await self.role_repository.get_role_by_name(self.db, role_name)

        if not role:
            raise RoleNotFoundError(f"Р РѕР»СЊ '{role_name}' РЅРµ РЅР°Р№РґРµРЅР° РІ Р±Р°Р·Рµ РґР°РЅРЅС‹С….")

        # 3. Р”РµР»РµРіРёСЂСѓРµРј Р»РѕРіРёРєСѓ РђРіСЂРµРіР°С‚Сѓ
        user.remove_role(role)

        # 4. РљРѕРјРјРёС‚
        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)

    async def get_user_roles(
        self,
        user_id: int,
    ) -> Sequence[str]:
        """РџРѕР»СѓС‡РёС‚СЊ РІСЃРµ СЂРѕР»Рё РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
        return await self.user_repository.get_user_roles(self.db, user_id)

    async def get_user_by_phone(
        self,
        phone: str,
    ) -> User | None:
        return await self.user_repository.get_user_by_phone(self.db, phone)

    async def get_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        user = await self.user_repository.get_user_by_telegram_id(self.db, tg_id)
        if user:
            return await map_orm_user_to_user_read_dto(user)
        else:
            return None

    async def add_user_role(
        self,
        telegram_id: int,
        new_role: RoleEnum,
    ) -> UserReadDTO:
        """
        РР·РјРµРЅРёС‚СЊ СЂРѕР»СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ.

        Args:
            telegram_id: ID РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РІ Telegram
            new_role: РќРѕРІР°СЏ СЂРѕР»СЊ (Student, Mentor, Admin)
            reason: РџСЂРёС‡РёРЅР° РёР·РјРµРЅРµРЅРёСЏ (РѕРїС†РёРѕРЅР°Р»СЊРЅРѕ)

        Returns:
            РћР±РЅРѕРІР»РµРЅРЅС‹Рµ РґР°РЅРЅС‹Рµ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ

        Raises:
            UserNotFoundError: Р•СЃР»Рё РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ
            RoleNotFoundError: Р•СЃР»Рё СЂРѕР»СЊ РЅРµ СЃСѓС‰РµСЃС‚РІСѓРµС‚
            InvalidRoleChangeError: Р•СЃР»Рё РёР·РјРµРЅРµРЅРёРµ СЂРѕР»Рё РЅРµРІРѕР·РјРѕР¶РЅРѕ
        """
        # РџРѕР»СѓС‡Р°РµРј РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
        user = await self.user_repository.get_by_telegram_id(self.db, telegram_id)
        if not user:
            raise UserNotFoundError(telegram_id=telegram_id)

        role = await self.role_repository.get_role_by_name(self.db, new_role.value)

        if not role:
            raise RoleNotFoundError(new_role.value)

        user.add_role(role)

        self.db.add(user)

        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)

    async def get_users_with_competence_id(self, competence_id: int) -> Sequence[UserReadDTO]:
        users = await self.user_repository.get_all_users_with_competence_id(self.db, competence_id)
        return [await map_orm_user_to_user_read_dto(user) for user in users]

    async def get_user_competencies(self, user_id: int) -> Sequence[CompetenceReadDTO]:
        user = await self.user_repository.get_by_id(self.db, user_id)
        if user is None:
            raise UserNotFoundError(user_id=user_id)
        competencies = await self.user_repository.get_all_user_competencies(self.db, user_id)
        return await map_orm_competencies_to_competence_read_dtos(competencies)

    async def add_user_competencies_by_names(self, user_id: int, competence_names: Sequence[str]) -> UserReadDTO:
        user = await self.user_repository.get_by_id(self.db, user_id)
        if user is None:
            raise UserNotFoundError(user_id=user_id)
        normalized_names = self._normalize_competence_names(competence_names)

        competencies = await self.competence_repository.get_by_names(self.db, normalized_names)
        found_names = {competence.name.strip().lower() for competence in competencies}
        missing_names = [name for name in normalized_names if name not in found_names]
        if missing_names:
            raise ValueError(f"Competence names not found: {missing_names}")

        user.add_competencies(competencies)
        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def remove_user_competencies_by_names(self, user_id: int, competence_names: Sequence[str]) -> UserReadDTO:
        user = await self.user_repository.get_by_id(self.db, user_id)
        if user is None:
            raise UserNotFoundError(user_id=user_id)
        normalized_names = self._normalize_competence_names(competence_names)

        competencies = await self.competence_repository.get_by_names(self.db, normalized_names)
        found_names = {competence.name.strip().lower() for competence in competencies}
        missing_names = [name for name in normalized_names if name not in found_names]
        if missing_names:
            raise ValueError(f"Competence names not found: {missing_names}")

        user.remove_competencies(competencies)
        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def add_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        user = await self.user_repository.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id=user_id)

        normalized_ids = sorted(set(competence_ids))
        if normalized_ids:
            competencies = await self.competence_repository.get_by_ids(self.db, normalized_ids)
            found_ids = {competence.id for competence in competencies}
            missing_ids = [competence_id for competence_id in normalized_ids if competence_id not in found_ids]
            if missing_ids:
                raise ValueError(f"Competence ids not found: {missing_ids}")
            user.add_competencies(competencies)

        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def remove_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        user = await self.user_repository.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id=user_id)

        normalized_ids = sorted(set(competence_ids))
        if normalized_ids:
            competencies = await self.competence_repository.get_by_ids(self.db, normalized_ids)
            found_ids = {competence.id for competence in competencies}
            missing_ids = [competence_id for competence_id in normalized_ids if competence_id not in found_ids]
            if missing_ids:
                raise ValueError(f"Competence ids not found: {missing_ids}")
            user.remove_competencies(competencies)

        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def update_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        user = await self.user_repository.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id=user_id)

        current_competencies = await self.user_repository.get_all_user_competencies(self.db, user_id)
        user.remove_competencies(current_competencies)

        normalized_ids = sorted(set(competence_ids))
        if normalized_ids:
            competencies = await self.competence_repository.get_by_ids(self.db, normalized_ids)
            found_ids = {competence.id for competence in competencies}
            missing_ids = [competence_id for competence_id in normalized_ids if competence_id not in found_ids]
            if missing_ids:
                raise ValueError(f"Competence ids not found: {missing_ids}")
            user.add_competencies(competencies)

        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)


async def get_user_by_telegram_id(db: AsyncSession, tg_id: int) -> UserReadDTO | None:
    """РџРѕР»СѓС‡РёС‚СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РїРѕ Telegram ID"""
    result = await db.execute(select(User).where(User.telegram_id == tg_id))
    user = result.scalar_one_or_none()
    if user:
        return await map_orm_user_to_user_read_dto(user)
    else:
        return None


async def create_user_profile(
    db: AsyncSession,
    *,
    data: UserCreateDTO,
) -> UserReadDTO:
    """РЎРѕР·РґР°РµС‚ РїСЂРѕС„РёР»СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ СЃ РЅР°С‡Р°Р»СЊРЅС‹РјРё СѓСЂРѕРІРЅСЏРјРё"""

    # РџРѕР»СѓС‡Р°РµРј РІСЃРµ СѓСЂРѕРІРЅРё
    all_levels = await get_all_levels(db)

    if not all_levels:
        raise ValueError("РќР°С‡Р°Р»СЊРЅС‹Рµ СѓСЂРѕРІРЅРё РЅРµ РЅР°Р№РґРµРЅС‹ РІ Р‘Р”!")

    # РџРѕР»СѓС‡Р°РµРј С‚РѕР»СЊРєРѕ РЅР°С‡Р°Р»СЊРЅС‹Р№ СѓСЂРѕРІРµРЅСЊ РґР»СЏ РєР°Р¶РґРѕРіРѕ С‚РёРїР°
    initial_levels = {}
    for level in all_levels:
        if level.level_type not in initial_levels:
            initial_levels[level.level_type] = level

    # РЎРѕР·РґР°РµРј РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
    user = User(
        phone_number=data.phone,
        telegram_id=data.tg_id,
        first_name=data.first_name,
        last_name=data.last_name,
        patronymic=data.patronymic,
    )

    db.add(user)
    await db.flush()

    # Р”РѕР±Р°РІР»СЏРµРј РўРћР›Р¬РљРћ РЅР°С‡Р°Р»СЊРЅС‹Рµ СѓСЂРѕРІРЅРё
    for level in initial_levels.values():
        user_level = UserLevel(user_id=user.id, level_id=level.id)
        db.add(user_level)

    await db.commit()
    await db.refresh(user)

    return await map_orm_user_to_user_read_dto(user)


async def update_user_points_by_id(
    db: AsyncSession,
    user_id: int,
    points_value: int,
    points_type: LevelTypeEnum,
) -> UserReadDTO:
    """РћР±РЅРѕРІРёС‚СЊ Р±Р°Р»Р»С‹ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise ValueError(f"РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ СЃ ID {user_id} РЅРµ РЅР°Р№РґРµРЅ.")

    if points_type == LevelTypeEnum.ACADEMIC:
        user.academic_points += points_value
        user.academic_points = max(user.academic_points, 0)
    elif points_type == LevelTypeEnum.REPUTATION:
        user.reputation_points += points_value
        user.reputation_points = max(user.reputation_points, 0)
    else:
        raise ValueError("РќРµРёР·РІРµСЃС‚РЅС‹Р№ С‚РёРї Р±Р°Р»Р»РѕРІ.")

    await db.commit()
    await db.refresh(user)
    return await map_orm_user_to_user_read_dto(user)


#   !!!   РќСѓР¶РЅРѕ РґРѕСЂР°Р±РѕС‚Р°С‚СЊ
async def collect_user_profile(db: AsyncSession, user_read_dto: UserReadDTO) -> UserProfileReadDTO:
    """РЎРѕР±РёСЂР°РµС‚ РїСЂРѕС„РёР»СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ"""
    levels_data = dict()
    for level_system in LevelTypeEnum:
        orm_current_level_res = await get_user_current_level(db, user_read_dto.id, level_system)
        if orm_current_level_res is None:
            raise ValueError(
                f"РЈСЂРѕРІРµРЅСЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ (id:{user_read_dto.id}) РЅРµ Р±С‹Р» РЅР°Р№РґРµРЅ "
            )

        _, orm_current_level = orm_current_level_res

        dto_current_level = await map_orm_level_to_level_read_dto(orm_current_level)

        orm_next_level = await get_next_level(db, orm_current_level, level_system)
        if orm_next_level is None:
            dto_next_level = dto_current_level
        else:
            dto_next_level = await map_orm_level_to_level_read_dto(orm_next_level)

        user_level = UserLevelReadDTO(
            system=level_system,
            current_level=dto_current_level,
            next_level=dto_next_level,
        )
        levels_data[level_system] = user_level

    return UserProfileReadDTO(user=user_read_dto, level_info=levels_data)
