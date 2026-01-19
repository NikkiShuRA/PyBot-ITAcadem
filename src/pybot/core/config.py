from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Конфигурация бота с валидацией и типизацией"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Telegram settings
    bot_token: str = Field(..., alias="BOT_TOKEN", description="Токен основного бота")
    bot_token_test: str = Field(..., alias="BOT_TOKEN_TEST", description="Токен тестового бота")
    # Database settings
    database_url: str = Field(..., alias="DATABASE_URL", description="URL базы данных")

    log_level: str = Field("INFO", alias="LOG_LEVEL", description="Уровень логирования")
    debug: bool = Field(False, alias="DEBUG", description="Режим отладки")


settings: BotSettings = BotSettings()
