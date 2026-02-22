from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Конфигурация бота с валидацией и типизацией"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Admin Panel
    admin_panel_enabled: bool = Field(True, alias="ADMIN_PANEL_ENABLED")
    web_host: str = Field("127.0.0.1", alias="WEB_HOST")
    web_port: int = Field(8001, alias="WEB_PORT")
    # Telegram settings
    bot_token: str = Field(..., alias="BOT_TOKEN", description="Токен основного бота")
    bot_token_test: str = Field(..., alias="BOT_TOKEN_TEST", description="Токен тестового бота")
    # Database settings
    database_url: str = Field(..., alias="DATABASE_URL", description="URL базы данных")

    log_level: str = Field("INFO", alias="LOG_LEVEL", description="Уровень логирования")
    debug: bool = Field(False, alias="DEBUG", description="Режим отладки")

    # Rate-limiting settings
    enable_rate_limit: bool = Field(True, alias="ENABLE_RATE_LIMIT")

    # Лимиты (можно переопределить через .env)
    rate_limit_cheap: int = Field(30, alias="RATE_LIMIT_CHEAP")
    time_limit_cheap: int = Field(60, alias="TIME_LIMIT_CHEAP")

    rate_limit_moderate: int = Field(10, alias="RATE_LIMIT_MODERATE")
    time_limit_moderate: int = Field(60, alias="TIME_LIMIT_MODERATE")

    rate_limit_expensive: int = Field(3, alias="RATE_LIMIT_EXPENSIVE")
    time_limit_expensive: int = Field(300, alias="TIME_LIMIT_EXPENSIVE")

    max_user_limiters: int = Field(
        1000, alias="MAX_USER_LIMITERS", description="Максимальное количество лимитеров в кэше"
    )

    enable_logging_middleware: bool = Field(
        True, alias="ENABLE_LOGGING_MIDDLEWARE", description="Включить логгирующий middleware"
    )

    enable_user_activity_middleware: bool = Field(
        True,
        alias="ENABLE_USER_ACTIVITY_MIDDLEWARE",
        description="Включить middleware для отслеживания активности пользователей",
    )

    enable_role_middleware: bool = Field(
        True, alias="ENABLE_ROLE_MIDDLEWARE", description="Включить middleware для проверки ролей пользователей"
    )


settings: BotSettings = BotSettings()
