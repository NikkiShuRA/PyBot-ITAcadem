import asyncio

from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka
from yaspin import yaspin

from ..core import logger
from ..core.config import settings
from ..db.database import SessionLocal
from ..di.containers import setup_container
from .dialogs import user_router
from .handlers import (
    common_router,
    points_router,
    profile_router,
    roles_router,
)
from .middlewares import (
    DbSessionMiddleware,
    LoggerMiddleware,
    RateLimitMiddleware,
    RoleMiddleware,
    UserActivityMiddleware,
)


async def setup_dispatcher() -> Dispatcher:
    return Dispatcher()


async def setup_middlewares(dp: Dispatcher) -> None:
    if settings.enable_logging_middleware:
        logging_middleware = LoggerMiddleware(
            enabled=True,
        )

        dp.message.middleware(logging_middleware)
        dp.callback_query.middleware(logging_middleware)
        dp.inline_query.middleware(logging_middleware)

        logger.info("LoggerMiddleware enabled")
    else:
        logger.info("LoggerMiddleware disabled")

    if settings.enable_user_activity_middleware:
        dp.message.middleware(UserActivityMiddleware())
        dp.callback_query.middleware(UserActivityMiddleware())

        logger.info("UserActivityMiddleware enabled")
    else:
        logger.info("UserActivityMiddleware disabled")

    if settings.enable_role_middleware:
        dp.message.middleware(RoleMiddleware())
        dp.callback_query.middleware(RoleMiddleware())
        dp.inline_query.middleware(RoleMiddleware())

        logger.info("RoleMiddleware enabled")
    else:
        logger.info("RoleMiddleware disabled")

    if settings.enable_rate_limit:
        dp.update.middleware(RateLimitMiddleware())
        dp.message.middleware(RateLimitMiddleware())
        dp.callback_query.middleware(RateLimitMiddleware())

        logger.info("RateLimitMiddleware enabled")
    else:
        logger.info("RateLimitMiddleware disabled")

    dp.update.middleware(DbSessionMiddleware(SessionLocal))


async def setup_di(dp: Dispatcher) -> AsyncContainer:
    container = await setup_container()
    logger.debug("Container setup complete: {container}", container=container)
    setup_dishka(container, dp, auto_inject=True)
    return container


async def setup_bot(container: AsyncContainer) -> Bot:
    return await container.get(Bot)


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(common_router)
    dp.include_router(points_router)
    dp.include_router(profile_router)
    dp.include_router(user_router)
    dp.include_router(roles_router)
    setup_dialogs(dp)


async def tg_bot_main() -> None:
    """Main bot function with graceful shutdown."""
    container: AsyncContainer | None = None
    try:
        with yaspin(text="Bot initialization...", color="cyan") as sp:
            dp = await setup_dispatcher()
            container = await setup_di(dp)
            bot = await setup_bot(container)
            await setup_middlewares(dp)
            setup_handlers(dp)
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Starting bot")
            sp.ok("Bot started")
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        logger.info("Received cancellation signal")
        raise
    except Exception:
        logger.exception("Unexpected error")
        raise
    finally:
        logger.info("Graceful shutdown...")

        if container is not None:
            try:
                await container.close()
                logger.info("Dishka container closed")
            except Exception:
                logger.exception("Error while closing container")
