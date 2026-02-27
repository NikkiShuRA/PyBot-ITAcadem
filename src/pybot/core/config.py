from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator
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
    notification_backend: Literal["telegram", "logging"] = Field(
        "telegram",
        alias="NOTIFICATION_BACKEND",
        description="Notification backend: 'telegram' or 'logging'",
    )
    fsm_storage_backend: Literal["memory", "redis"] = Field(
        "memory",
        alias="FSM_STORAGE_BACKEND",
        description="FSM storage backend: 'memory' or 'redis'",
    )
    redis_url: str = Field(
        "redis://localhost:6379/0",
        alias="REDIS_URL",
        description="Redis URL used for FSM storage when FSM_STORAGE_BACKEND=redis",
    )
    # TODO: Replace default value with real admin Telegram ID in .env,
    # or switch to required Field(...) once all environments are configured.
    role_request_admin_tg_id: int = Field(
        0,
        alias="ROLE_REQUEST_ADMIN_TG_ID",
        description="Telegram user id of admin recipient for role requests",
    )
    auto_admin_telegram_ids: set[int] = Field(
        default_factory=set,
        alias="AUTO_ADMIN_TELEGRAM_IDS",
        description="Telegram user ids that receive Admin role automatically on registration",
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

    # Broadcast settings
    broadcast_bulk_size: int = Field(20, alias="BROADCAST_BULK_SIZE", ge=1, le=25)
    broadcast_max_concurrency: int = Field(5, alias="BROADCAST_MAX_CONCURRENCY", ge=1, le=10)
    broadcast_batch_pause_ms: int = Field(1200, alias="BROADCAST_BATCH_PAUSE_MS", ge=700, le=5000)
    broadcast_jitter_min_ms: int = Field(80, alias="BROADCAST_JITTER_MIN_MS", ge=50, le=1000)
    broadcast_jitter_max_ms: int = Field(160, alias="BROADCAST_JITTER_MAX_MS", ge=50, le=2000)
    broadcast_retry_attempts: int = Field(5, alias="BROADCAST_RETRY_ATTEMPTS", ge=1, le=10)
    broadcast_retry_max_wait_s: int = Field(30, alias="BROADCAST_RETRY_MAX_WAIT_S", ge=1, le=120)

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
    def active_bot_token(self: Self) -> str:
        """Return active bot token based on BOT_MODE."""
        if self.bot_mode == "prod":
            return self.bot_token
        return self.bot_token_test

    @model_validator(mode="after")
    def validate_broadcast_jitter_range(self: Self) -> Self:
        if self.broadcast_jitter_max_ms < self.broadcast_jitter_min_ms:
            raise ValueError("BROADCAST_JITTER_MAX_MS must be greater than or equal to BROADCAST_JITTER_MIN_MS")
        return self


settings: BotSettings = BotSettings()
