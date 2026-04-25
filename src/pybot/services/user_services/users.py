from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import BotSettings
from ...core.constants import RoleEnum
from ...domain.exceptions import InitialLevelsNotFoundError, RoleNotFoundError, UserNotFoundError
from ...dto import UserCreateDTO, UserReadDTO
from ...infrastructure.level_repository import LevelRepository
from ...infrastructure.role_repository import RoleRepository
from ...infrastructure.user_repository import UserRepository
from ...mappers.user_mappers import map_orm_user_to_user_read_dto


class UserService:
    """Общий сервис для работы с пользователями.

    Обеспечивает базовые операции: регистрацию, поиск и отслеживание активности.
    """

    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        level_repository: LevelRepository,
        role_repository: RoleRepository,
        settings: BotSettings,
    ) -> None:
        """Инициализирует сервис пользователей.

        Args:
            db: Асинхронная сессия базы данных.
            user_repository: Репозиторий пользователей.
            level_repository: Репозиторий уровней.
            role_repository: Репозиторий ролей.
            settings: Настройки бота.
        """
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.level_repository: LevelRepository = level_repository
        self.role_repository: RoleRepository = role_repository
        self._settings = settings

    async def register_student(self, dto: UserCreateDTO) -> UserReadDTO:
        """Регистрирует нового пользователя как студента (упрощенная версия).

        Назначает начальные уровни и базовую роль "Student".

        Args:
            dto: DTO с данными для создания профиля.

        Raises:
            InitialLevelsNotFoundError: Если начальные уровни не найдены.
            RoleNotFoundError: Если роль "Student" (или "Admin" при авто-выдаче) не найдена.

        Returns:
            UserReadDTO: DTO созданного пользователя.
        """
        initial_levels = await self.level_repository.find_initial_levels(self.db)

        if not initial_levels:
            raise InitialLevelsNotFoundError()

        student_role = await self.role_repository.find_role_by_name(self.db, "Student")
        if not student_role:
            raise RoleNotFoundError("Роль 'Student' не найдена в базе данных. Сначала создайте её!")

        user = await self.user_repository.create_user_profile(self.db, data=dto)
        user.set_initial_levels(initial_levels)
        user.add_role(student_role)

        if dto.tg_id in self._settings.auto_admin_telegram_ids:
            admin_role = await self.role_repository.find_role_by_name(self.db, RoleEnum.ADMIN.value)
            if not admin_role:
                raise RoleNotFoundError("Роль 'Admin' не найдена в базе данных. Сначала создайте её!")
            user.add_role(admin_role)

        self.db.add(user)
        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def get_user(
        self,
        user_id: int,
    ) -> UserReadDTO:
        """Получает пользователя по его внутреннему ID.

        Args:
            user_id: Идентификатор пользователя (PK).

        Raises:
            UserNotFoundError: Если пользователь не найден.

        Returns:
            UserReadDTO: DTO пользователя.
        """
        try:
            user = await self.user_repository.get_by_id(self.db, user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id) from err
        else:
            return await map_orm_user_to_user_read_dto(user)

    async def find_all_user_roles(self, user_id: int) -> set[str] | None:
        """Находит все роли пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            set[str] | None: Множество названий ролей или None, если ролей нет.
        """
        roles = await self.user_repository.find_all_user_roles_by_pk(self.db, user_id)
        return roles if roles else None

    async def find_user_by_phone(
        self,
        phone: str,
    ) -> UserReadDTO | None:
        """Ищет пользователя по номеру телефона.

        Args:
            phone: Номер телефона.

        Returns:
            UserReadDTO | None: DTO пользователя или None, если не найден.
        """
        user = await self.user_repository.find_user_by_phone(self.db, phone)
        if user:
            return await map_orm_user_to_user_read_dto(user)
        return None

    async def find_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        """Ищет пользователя по Telegram ID.

        Args:
            tg_id: Telegram ID пользователя.

        Returns:
            UserReadDTO | None: DTO пользователя или None, если не найден.
        """
        user = await self.user_repository.find_user_by_telegram_id(self.db, tg_id)
        if user:
            return await map_orm_user_to_user_read_dto(user)
        return None

    async def track_activity(self, telegram_id: int) -> int | None:
        """Обновляет дату последней активности пользователя.

        Args:
            telegram_id: Telegram ID пользователя.

        Returns:
            int | None: Внутренний ID пользователя или None, если пользователь не найден.
        """
        user = await self.user_repository.find_user_by_telegram_id(self.db, telegram_id)
        if not user:
            return None

        await self.user_repository.update_user_last_active(self.db, user.id)
        await self.db.commit()
        return user.id
