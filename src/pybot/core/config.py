from __future__ import annotations

import functools
from typing import Annotated, Any, Literal, Self, cast

from pydantic import Field, field_validator, model_validator
from pydantic_extra_types.cron import CronStr
from pydantic_extra_types.timezone_name import TimeZoneName
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from .constants import RoleEnum


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
    telegram_proxy_url: str | None = Field(
        None,
        alias="TELEGRAM_PROXY_URL",
        description="Optional proxy URL for Telegram Bot API traffic",
    )
    runtime_alerts_enabled: bool = Field(
        False,
        alias="RUNTIME_ALERTS_ENABLED",
        description="Enable runtime startup/shutdown alerts for the bot process",
    )
    runtime_alerts_chat_id: int | None = Field(
        None,
        alias="RUNTIME_ALERTS_CHAT_ID",
        description="Telegram chat id for runtime alerts",
        gt=0,
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
    role_request_admin_tg_id: int = Field(
        ...,
        alias="ROLE_REQUEST_ADMIN_TG_ID",
        description="Telegram user id of admin recipient for role requests",
        gt=0,
    )
    role_request_reject_cooldown_minutes: int = Field(
        1440,
        alias="ROLE_REQUEST_REJECT_COOLDOWN_MINUTES",
        description="Cooldown in minutes for role request rejection",
        gt=0,
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
    log_format: Literal["text", "json"] = Field(
        "text",
        alias="LOG_FORMAT",
        description=(
            "Log output format. Use 'text' for human-readable coloured output (default, dev/local), "
            "'json' for structured machine-readable output (recommended for production log collectors "
            "such as Loki, CloudWatch, or ELK)."
        ),
    )
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
    leaderboard_weekly_enabled: bool = Field(
        False,
        alias="LEADERBOARD_WEEKLY_ENABLED",
        description="Enable weekly leaderboard publication via TaskIQ scheduler",
    )
    leaderboard_weekly_recipient_id: int | None = Field(
        None,
        alias="LEADERBOARD_WEEKLY_RECIPIENT_ID",
        description="Transport recipient id for weekly leaderboard publication",
    )
    leaderboard_weekly_cron: CronStr = Field(
        default_factory=lambda: CronStr("0 9 * * 1"),
        alias="LEADERBOARD_WEEKLY_CRON",
        description="Cron expression for weekly leaderboard publication",
    )
    leaderboard_weekly_timezone: TimeZoneName = Field(
        default_factory=lambda: TimeZoneName("Asia/Yekaterinburg"),
        alias="LEADERBOARD_WEEKLY_TIMEZONE",
        description="Timezone used for weekly leaderboard cron scheduling",
    )
    leaderboard_weekly_limit: int = Field(
        10,
        alias="LEADERBOARD_WEEKLY_LIMIT",
        description="Max rows per leaderboard section in weekly publication",
        ge=1,
    )
    leaderboard_weekly_retry_enabled: bool = Field(
        True,
        alias="LEADERBOARD_WEEKLY_RETRY_ENABLED",
        description="Enable retry labels for weekly leaderboard task execution",
    )
    leaderboard_weekly_retry_max_retries: int = Field(
        3,
        alias="LEADERBOARD_WEEKLY_RETRY_MAX_RETRIES",
        description="Maximum retry attempts for weekly leaderboard task",
        ge=1,
    )
    leaderboard_weekly_retry_delay_s: int = Field(
        30,
        alias="LEADERBOARD_WEEKLY_RETRY_DELAY_S",
        description="Base retry delay in seconds for weekly leaderboard task",
        ge=1,
    )
    leaderboard_weekly_retry_use_jitter: bool = Field(
        True,
        alias="LEADERBOARD_WEEKLY_RETRY_USE_JITTER",
        description="Use jitter for weekly leaderboard retry delays",
    )
    leaderboard_weekly_retry_use_exponential_backoff: bool = Field(
        True,
        alias="LEADERBOARD_WEEKLY_RETRY_USE_EXPONENTIAL_BACKOFF",
        description="Use exponential backoff for weekly leaderboard retry delays",
    )
    leaderboard_weekly_retry_max_delay_s: int = Field(
        300,
        alias="LEADERBOARD_WEEKLY_RETRY_MAX_DELAY_S",
        description="Maximum retry delay in seconds for weekly leaderboard task",
        ge=1,
    )

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

    broadcast_allowed_roles: Annotated[set[str], NoDecode] = Field(
        default_factory=lambda: {"Admin"},
        alias="BROADCAST_ALLOWED_ROLES",
        description="Broadcast allowed roles",
    )

    broadcast_max_text_length: int = Field(
        4093,
        alias="BROADCAST_MAX_TEXT_LENGTH",
        description="Broadcast body length before adding crop suffix",
        ge=1,
        le=4096,
    )

    @property
    def active_bot_token(self: Self) -> str:
        """Return active bot token based on BOT_MODE."""
        if self.bot_mode == "prod":
            return self.bot_token
        return self.bot_token_test

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_flag(cls, value: bool | str | int) -> bool:
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            return value != 0

        normalized = value.strip().lower()
        if normalized in {"1", "true", "t", "yes", "y", "on", "debug"}:
            return True
        if normalized in {"0", "false", "f", "no", "n", "off", "release"}:
            return False

        raise ValueError("DEBUG must be a boolean-like value (e.g. true/false/debug/release)")

    @field_validator("telegram_proxy_url", mode="before")
    @classmethod
    def parse_telegram_proxy_url(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            return None
        return normalized

    @field_validator("leaderboard_weekly_recipient_id", mode="before")
    @classmethod
    def parse_weekly_recipient_id(cls, value: int | str | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return None
            return int(normalized)
        return value

    @field_validator("leaderboard_weekly_recipient_id")
    @classmethod
    def validate_weekly_recipient_id(cls, value: int | None) -> int | None:
        if value == 0:
            raise ValueError("LEADERBOARD_WEEKLY_RECIPIENT_ID must not be equal to 0")
        return value

    @field_validator("broadcast_allowed_roles", mode="before")
    @classmethod
    def parse_broadcast_allowed_roles(cls, value: object) -> set[str]:
        if isinstance(value, set):
            roles = {str(role).strip() for role in value if str(role).strip()}
            return cls._validate_roles(roles)

        if isinstance(value, list | tuple):
            roles = {str(role).strip() for role in value if str(role).strip()}
            return cls._validate_roles(roles)

        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return set()

            # Supports both "Admin,Mentor" and JSON-like '["Admin","Mentor"]'.
            normalized = normalized.strip("[]")
            tokens = (token.strip().strip("\"'") for token in normalized.split(","))
            roles = {token for token in tokens if token}
            return cls._validate_roles(roles)

        raise ValueError("BROADCAST_ALLOWED_ROLES must be a comma-separated string or a sequence")

    @staticmethod
    def _validate_roles(roles: set[str]) -> set[str]:
        available_roles = {role.value for role in RoleEnum}
        unknown_roles = roles - available_roles
        if unknown_roles:
            sorted_roles = ", ".join(sorted(unknown_roles))
            raise ValueError(f"Unknown role(s) in BROADCAST_ALLOWED_ROLES: {sorted_roles}")
        return roles

    @model_validator(mode="after")
    def validate_broadcast_jitter_range(self: Self) -> Self:
        if self.broadcast_jitter_max_ms < self.broadcast_jitter_min_ms:
            raise ValueError("BROADCAST_JITTER_MAX_MS must be greater than or equal to BROADCAST_JITTER_MIN_MS")
        return self

    @model_validator(mode="after")
    def validate_runtime_alerts_config(self: Self) -> Self:
        if self.runtime_alerts_enabled and self.runtime_alerts_chat_id is None:
            raise ValueError("RUNTIME_ALERTS_CHAT_ID must be set when RUNTIME_ALERTS_ENABLED=true")
        return self

    @model_validator(mode="after")
    def validate_weekly_leaderboard_config(self: Self) -> Self:
        if self.leaderboard_weekly_enabled and self.leaderboard_weekly_recipient_id is None:
            raise ValueError("LEADERBOARD_WEEKLY_RECIPIENT_ID must be set when LEADERBOARD_WEEKLY_ENABLED=true")
        return self

    @model_validator(mode="after")
    def validate_weekly_leaderboard_retry_config(self: Self) -> Self:
        if self.leaderboard_weekly_retry_max_delay_s < self.leaderboard_weekly_retry_delay_s:
            raise ValueError(
                "LEADERBOARD_WEEKLY_RETRY_MAX_DELAY_S must be greater than or equal to LEADERBOARD_WEEKLY_RETRY_DELAY_S"
            )
        return self


@functools.lru_cache(maxsize=1)
def get_settings() -> BotSettings:
    """Return the application settings as a cached singleton."""
    return BotSettings()


class SettingsProxy:
    """Lazy proxy to defer BotSettings evaluation until an attribute is actually accessed."""

    def __getattr__(self, name: str) -> Any:
        return getattr(get_settings(), name)


settings: BotSettings = cast(BotSettings, SettingsProxy())
