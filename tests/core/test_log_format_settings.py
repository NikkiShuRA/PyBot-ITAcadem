from __future__ import annotations

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from pybot.core.config import BotSettings

ADMIN_TG_ID = 123_456_789


class BotSettingsWithoutDotenv(BotSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings, env_settings)


def test_log_format_defaults_to_text_for_test_mode() -> None:
    parsed_settings = BotSettingsWithoutDotenv(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        BOT_MODE="test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
    )

    assert parsed_settings.log_format == "text"


def test_log_format_defaults_to_json_for_prod_mode() -> None:
    parsed_settings = BotSettingsWithoutDotenv(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        BOT_MODE="prod",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
    )

    assert parsed_settings.log_format == "json"


def test_explicit_log_format_overrides_prod_runtime_default() -> None:
    parsed_settings = BotSettingsWithoutDotenv(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        BOT_MODE="prod",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
        LOG_FORMAT="text",
    )

    assert parsed_settings.log_format == "text"
