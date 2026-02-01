from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from dishka.integrations.aiogram import (
    setup_dishka,
)
from yaspin import yaspin

from ..core import logger
from ..core.config import settings
from ..db.database import SessionLocal
from ..di.containers import setup_container
from .dialogs import user_router
from .handlers import (
    common_router,
    points_router,
    profile_router,  # !!! Костыль вывода профиля (Нужно перепроверить и улучшить)
)
from .middlewares import (
    DbSessionMiddleware,
    LoggerMiddleware,
    RateLimitMiddleware,
    RoleMiddleware,
    UserActivityMiddleware,
)


# TODO Разделить это на отдельные функции для инициализации разных частей бота (middlewares, роутеры и т.д.)
async def tg_bot_main() -> None:
    with yaspin(text="Инициализация бота...", color="cyan") as sp:
        bot = Bot(settings.bot_token_test)
        dp = Dispatcher()
        if settings.enable_logging_middleware:
            logging_middleware = LoggerMiddleware(
                enabled=True,
            )

            dp.message.middleware(logging_middleware)
            dp.callback_query.middleware(logging_middleware)
            dp.inline_query.middleware(logging_middleware)

            logger.info("✅ LoggerMiddleware включён")
        else:
            logger.info("⚠️ LoggerMiddleware отключён")

        if settings.enable_user_activity_middleware:
            dp.message.middleware(UserActivityMiddleware())
            dp.callback_query.middleware(UserActivityMiddleware())

            logger.info("✅ UserActivityMiddleware включён")
        else:
            logger.info("⚠️ UserActivityMiddleware отключён")

        if settings.enable_role_middleware:
            dp.message.middleware(RoleMiddleware())
            dp.callback_query.middleware(RoleMiddleware())
            dp.inline_query.middleware(RoleMiddleware())

            logger.info("✅ RoleMiddleware включён")
        else:
            logger.info("⚠️ RoleMiddleware отключён")

        if settings.enable_rate_limit:
            dp.update.middleware(RateLimitMiddleware())
            dp.message.middleware(RateLimitMiddleware())
            dp.callback_query.middleware(RateLimitMiddleware())

            logger.info("✅ RateLimitMiddleware включён")
        else:
            logger.info("⚠️ RateLimitMiddleware отключён")

        dp.update.middleware(DbSessionMiddleware(SessionLocal))

        # Подключаем остальные роутеры common
        dp.include_router(common_router)
        dp.include_router(points_router)
        dp.include_router(profile_router)  # !!! Костыль вывода профиля (Нужно перепроверить и улучшить)
        dp.include_router(user_router)

        # Инициализируем DialogManager для работы с диалогами
        setup_dialogs(dp)
        container = await setup_container()
        logger.debug("🚩 Container setup complete: {container}", container=container)
        setup_dishka(container, dp, auto_inject=True)
        dp.shutdown.register(container.close)
        # сбросить накопившиеся апдейты
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("Запуск бота")
        sp.ok("✅ Бот запущен!")
    await dp.start_polling(bot)
