from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Telegram settings
    bot_token: str = Field(..., alias="BOT_TOKEN", description="Production bot token")
    bot_token_test: str = Field(..., alias="BOT_TOKEN_TEST", description="Test bot token")
    bot_mode: Literal["test", "prod"] = Field(
        "test",
        alias="BOT_MODE",
        description="Bot runtime mode: 'test' uses BOT_TOKEN_TEST, 'prod' uses BOT_TOKEN",
    )
    # TODO: Replace default value with real admin Telegram ID in .env,
    # or switch to required Field(...) once all environments are configured.
    role_request_admin_tg_id: int = Field(
        0,
        alias="ROLE_REQUEST_ADMIN_TG_ID",
        description="Telegram user id of admin recipient for role requests",
    )

    # Database settings
    database_url: str = Field(..., alias="DATABASE_URL", description="Database URL")

    # General settings
    log_level: str = Field("INFO", alias="LOG_LEVEL", description="Logging level")
    debug: bool = Field(False, alias="DEBUG", description="Debug mode")

    # Rate limit settings
    enable_rate_limit: bool = Field(True, alias="ENABLE_RATE_LIMIT")
    rate_limit_cheap: int = Field(30, alias="RATE_LIMIT_CHEAP")
    time_limit_cheap: int = Field(60, alias="TIME_LIMIT_CHEAP")
    rate_limit_moderate: int = Field(10, alias="RATE_LIMIT_MODERATE")
    time_limit_moderate: int = Field(60, alias="TIME_LIMIT_MODERATE")
    rate_limit_expensive: int = Field(3, alias="RATE_LIMIT_EXPENSIVE")
    time_limit_expensive: int = Field(300, alias="TIME_LIMIT_EXPENSIVE")
    max_user_limiters: int = Field(1000, alias="MAX_USER_LIMITERS", description="Limiter cache size")

    # Middleware toggles
    enable_logging_middleware: bool = Field(
        True,
        alias="ENABLE_LOGGING_MIDDLEWARE",
        description="Enable logging middleware",
    )
    enable_user_activity_middleware: bool = Field(
        True,
        alias="ENABLE_USER_ACTIVITY_MIDDLEWARE",
        description="Enable user activity middleware",
    )
    enable_role_middleware: bool = Field(
        True,
        alias="ENABLE_ROLE_MIDDLEWARE",
        description="Enable role-check middleware",
    )

    # Health API settings
    health_api_enabled: bool = Field(
        False,
        alias="HEALTH_API_ENABLED",
        description="Enable separate FastAPI health endpoints process",
    )
    health_api_host: str = Field(
        "localhost",
        alias="HEALTH_API_HOST",
        description="Health API host",
    )
    health_api_port: int = Field(
        8001,
        alias="HEALTH_API_PORT",
        description="Health API port",
    )

    @property
    def active_bot_token(self) -> str:
        """Return active bot token based on BOT_MODE."""
        if self.bot_mode == "prod":
            return self.bot_token
        return self.bot_token_test


settings: BotSettings = BotSettings()
