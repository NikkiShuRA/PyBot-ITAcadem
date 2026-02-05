from collections.abc import AsyncGenerator

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from ..core import logger
from ..db.database import engine as global_engine
from ..domain.services.level_calculator import LevelCalculator
from ..infrastructure.level_repository import LevelRepository
from ..infrastructure.role_repository import RoleRepository
from ..infrastructure.user_repository import UserRepository
from ..infrastructure.valuation_repository import ValuationRepository
from ..services.points import PointsService
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


class DomainServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def level_calculator(self) -> LevelCalculator:
        """Domain Service для расчета уровней."""
        return LevelCalculator()


async def setup_container() -> AsyncContainer:
    """Собрать контейнер."""
    return make_async_container(
        DatabaseProvider(),
        SessionProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        AiogramProvider(),
        DomainServiceProvider(),
    )
