from __future__ import annotations

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Конфигурация бота с валидацией и типизацией"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Telegram settings
    bot_token: str = Field(..., alias="BOT_TOKEN", description="Токен основного бота")
    bot_token_test: str = Field(..., alias="BOT_TOKEN_TEST", description="Токен тестового бота")
    # Database settings
    db_user: str = Field(..., alias="DB_USER", description="Пользователь PostgreSQL")
    db_pass: str = Field(..., alias="DB_PASS", description="Пароль PostgreSQL")
    db_host: str = Field("localhost", alias="DB_HOST", description="Хост PostgreSQL")
    db_port: int = Field(5432, alias="DB_PORT", description="Порт PostgreSQL")
    db_name: str = Field(..., alias="DB_NAME", description="Имя базы данных")

    database_url: str | None = None

    log_level: str = Field("INFO", alias="LOG_LEVEL", description="Уровень логирования")
    debug: bool = Field(False, alias="DEBUG", description="Режим отладки")

    @model_validator(mode="after")
    def assemble_db_url(self) -> BotSettings:
        """Автоматически формирует URL для подключения к БД"""
        if self.database_url is None:
            self.database_url = (
                f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        return self


settings: BotSettings = BotSettings()  # type: ignore[call-arg]
