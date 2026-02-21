from collections.abc import AsyncGenerator

from aiogram import Bot
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from ..core import logger
from ..core.config import settings
from ..db.database import engine as global_engine
from ..domain.services.level_calculator import LevelCalculator
from ..infrastructure import LevelRepository, RoleRepository, RoleRequestRepository, UserRepository, ValuationRepository
from ..services.points import PointsService
from ..services.role_request import RoleRequestService
from ..services.users import UserService


class DatabaseProvider(Provider):
    """Провайдеры для БД."""

    @provide(scope=Scope.APP)
    async def engine(self) -> AsyncEngine:
        """Создать Engine ОДИН раз."""
        return global_engine

    async def close(self, engine: AsyncEngine) -> None:
        """Закрыть engine при shutdown контейнера."""
        await engine.dispose()
        logger.info("✅ Database engine disposed")


class SessionProvider(Provider):
    """Провайдер для сессий — НОВАЯ сессия на каждый запрос!"""

    @provide(scope=Scope.REQUEST)
    async def session(self, engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
        """
        Создать НОВУЮ сессию для КАЖДОГО update'а.

        1️⃣  Dishka видит: "нужна AsyncEngine"
        2️⃣  Dishka берет его из APP scope
        3️⃣  Создает новую сессию
        4️⃣  Передает в хэндлер/callback
        5️⃣  После хэндлера → автоматически закрывается
        """
        async_session_maker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with async_session_maker() as session:
            yield session


class RepositoryProvider(Provider):
    """Репозитории — stateless, живут всю программу."""

    @provide(scope=Scope.APP)
    def user_repository(self) -> UserRepository:
        """
        ⚠️  ВАЖНО: репозиторий создается БЕЗ сессии!

        Сессия будет внедрена позже в методы.
        Репозиторий — это просто "конструктор запросов".
        """
        return UserRepository()

    @provide(scope=Scope.APP)
    def level_repository(self) -> LevelRepository:
        """
        ⚠️  ВАЖНО: репозиторий создается БЕЗ сессии!

        Сессия будет внедрена позже в методы.
        Репозиторий — это просто "конструктор запросов".
        """
        return LevelRepository()

    @provide(scope=Scope.APP)
    def valuation_reposiory(self) -> ValuationRepository:
        """
        ⚠️  ВАЖНО: репозиторий создается БЕЗ сессии!

        Сессия будет внедрена позже в методы.
        Репозиторий — это просто "конструктор запросов".
        """
        return ValuationRepository()

    @provide(scope=Scope.APP)
    def role_repository(self) -> RoleRepository:
        """
        ⚠️  ВАЖНО: репозиторий создается БЕЗ сессии!

        Сессия будет внедрена позже в методы.
        Репозиторий — это просто "конструктор запросов".
        """
        return RoleRepository()

    @provide(scope=Scope.APP)
    def role_request_repository(self) -> RoleRequestRepository:
        return RoleRequestRepository()


class ServiceProvider(Provider):
    """Сервисы — бизнес-логика."""

    @provide(scope=Scope.REQUEST)
    def user_service(
        self,
        db: AsyncSession,  # ← Новая сессия на каждый запрос
        user_repository: UserRepository,  # ← Берется из APP scope
        level_repository: LevelRepository,  # ← Берется из APP scope
        role_repository: RoleRepository,  # ← Берется из APP scope
    ) -> UserService:
        """Сервис получает репозиторий один раз."""
        return UserService(db, user_repository, level_repository, role_repository)

    @provide(scope=Scope.REQUEST)
    def points_service(
        self,
        db: AsyncSession,
        level_calculator: LevelCalculator,
        user_repository: UserRepository,
        level_repository: LevelRepository,
        role_repository: RoleRepository,
    ) -> "PointsService":
        """Сервис получает репозиторий один раз."""
        return PointsService(db, level_calculator, user_repository, level_repository)

    @provide(scope=Scope.REQUEST)
    def role_request_service(
        self,
        db: AsyncSession,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        role_request_repository: RoleRequestRepository,
    ) -> RoleRequestService:
        return RoleRequestService(db, role_repository, user_repository, role_request_repository)


class DomainServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def level_calculator(self) -> LevelCalculator:
        """Domain Service для расчета уровней."""
        return LevelCalculator()


class BotProvider(Provider):
    @provide(scope=Scope.APP)
    async def bot(self) -> AsyncGenerator[Bot, None]:
        bot = Bot(settings.bot_token_test)
        try:
            yield bot
        finally:
            await bot.session.close()
            logger.info("Bot session closed")


async def setup_container() -> AsyncContainer:
    """Собрать контейнер."""
    return make_async_container(
        DatabaseProvider(),
        SessionProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        AiogramProvider(),
        DomainServiceProvider(),
        BotProvider(),
    )
