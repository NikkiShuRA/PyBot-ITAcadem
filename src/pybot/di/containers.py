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
from ..infrastructure.ports import TelegramNotificationService
from ..services.health import HealthService, SessionExecutor
from ..services.points import PointsService
from ..services.ports import NotificationPort
from ..services.role_request import RoleRequestService
from ..services.users import UserService


class DatabaseProvider(Provider):
    """Providers for database resources."""

    @provide(scope=Scope.APP)
    async def engine(self) -> AsyncGenerator[AsyncEngine, None]:
        """Provide one SQLAlchemy engine for the whole app lifecycle."""
        engine = global_engine
        try:
            yield engine
        finally:
            await engine.dispose()
            logger.info("Database engine disposed")


class SessionProvider(Provider):
    """Provide one DB session per request/update."""

    @provide(scope=Scope.REQUEST)
    async def session(self, engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
        """Create request-scoped async SQLAlchemy session."""
        session_maker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with session_maker() as session:
            yield session


class RepositoryProvider(Provider):
    """Stateless repositories with APP scope."""

    @provide(scope=Scope.APP)
    def user_repository(self) -> UserRepository:
        return UserRepository()

    @provide(scope=Scope.APP)
    def level_repository(self) -> LevelRepository:
        return LevelRepository()

    @provide(scope=Scope.APP)
    def valuation_reposiory(self) -> ValuationRepository:
        return ValuationRepository()

    @provide(scope=Scope.APP)
    def role_repository(self) -> RoleRepository:
        return RoleRepository()

    @provide(scope=Scope.APP)
    def role_request_repository(self) -> RoleRequestRepository:
        return RoleRequestRepository()


class ServiceProvider(Provider):
    """Application services."""

    @provide(scope=Scope.REQUEST)
    def user_service(
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        level_repository: LevelRepository,
        role_repository: RoleRepository,
    ) -> UserService:
        return UserService(db, user_repository, level_repository, role_repository)

    @provide(scope=Scope.REQUEST)
    def points_service(
        self,
        db: AsyncSession,
        level_calculator: LevelCalculator,
        user_repository: UserRepository,
        level_repository: LevelRepository,
        role_repository: RoleRepository,
    ) -> PointsService:
        return PointsService(db, level_calculator, user_repository, level_repository)

    @provide(scope=Scope.REQUEST)
    def role_request_service(
        self,
        db: AsyncSession,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        role_request_repository: RoleRequestRepository,
        notification_service: NotificationPort,
    ) -> RoleRequestService:
        return RoleRequestService(db, role_repository, user_repository, role_request_repository, notification_service)


class HealthProvider(Provider):
    """Health API services."""

    @provide(scope=Scope.REQUEST)
    def health_service(self, db: AsyncSession) -> HealthService:
        return HealthService(SessionExecutor(db))


class DomainServiceProvider(Provider):
    """Domain services."""

    @provide(scope=Scope.APP)
    def level_calculator(self) -> LevelCalculator:
        return LevelCalculator()


class BotProvider(Provider):
    """Telegram Bot provider with APP scope."""

    @provide(scope=Scope.APP)
    async def bot(self) -> AsyncGenerator[Bot, None]:
        bot = Bot(settings.active_bot_token)
        try:
            yield bot
        finally:
            await bot.session.close()
            logger.info("Bot session closed")


class PortsProvider(Provider):
    @provide(scope=Scope.APP)
    def notification_port(self, bot: Bot) -> NotificationPort:
        return TelegramNotificationService(bot)


async def setup_container() -> AsyncContainer:
    """Build the app DI container."""
    return make_async_container(
        DatabaseProvider(),
        SessionProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        AiogramProvider(),
        DomainServiceProvider(),
        BotProvider(),
        PortsProvider(),
    )


def setup_health_container() -> AsyncContainer:
    """Build DI container for health API (minimal set)."""
    return make_async_container(
        DatabaseProvider(),
        SessionProvider(),
        HealthProvider(),
    )
