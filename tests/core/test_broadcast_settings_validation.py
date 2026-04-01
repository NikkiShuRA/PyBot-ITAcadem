import pytest
from pydantic import ValidationError
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


def test_broadcast_jitter_range_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_JITTER_MAX_MS"):
        BotSettingsWithoutDotenv(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
            BROADCAST_JITTER_MIN_MS=200,
            BROADCAST_JITTER_MAX_MS=100,
        )


def test_broadcast_bulk_size_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_BULK_SIZE"):
        BotSettingsWithoutDotenv(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
            BROADCAST_BULK_SIZE=0,
        )


def test_broadcast_batch_pause_min_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_BATCH_PAUSE_MS"):
        BotSettingsWithoutDotenv(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
            BROADCAST_BATCH_PAUSE_MS=600,
        )


def test_broadcast_max_text_length_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_MAX_TEXT_LENGTH"):
        BotSettingsWithoutDotenv(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
            BROADCAST_MAX_TEXT_LENGTH=0,
        )


def test_auto_admin_telegram_ids_parsed_from_json_array(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTO_ADMIN_TELEGRAM_IDS", "[123456789,987654321,123456789]")

    parsed_settings = BotSettingsWithoutDotenv(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
    )

    assert parsed_settings.auto_admin_telegram_ids == {123456789, 987654321}


def test_broadcast_allowed_roles_parsed_from_comma_separated_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROADCAST_ALLOWED_ROLES", "Admin,Mentor,Admin")

    parsed_settings = BotSettingsWithoutDotenv(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
    )

    assert parsed_settings.broadcast_allowed_roles == {"Admin", "Mentor"}


def test_broadcast_allowed_roles_default_is_admin() -> None:
    parsed_settings = BotSettingsWithoutDotenv(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
    )

    assert parsed_settings.broadcast_allowed_roles == {"Admin"}


def test_telegram_proxy_url_defaults_to_none() -> None:
    parsed_settings = BotSettingsWithoutDotenv(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
    )

    assert parsed_settings.telegram_proxy_url is None


def test_telegram_proxy_url_is_parsed_from_env_var() -> None:
    parsed_settings = BotSettingsWithoutDotenv(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
        TELEGRAM_PROXY_URL="socks5://127.0.0.1:1080",
    )

    assert parsed_settings.telegram_proxy_url == "socks5://127.0.0.1:1080"


def test_runtime_alerts_default_to_disabled_without_chat_id() -> None:
    parsed_settings = BotSettingsWithoutDotenv(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
    )

    assert parsed_settings.runtime_alerts_enabled is False
    assert parsed_settings.runtime_alerts_chat_id is None


def test_runtime_alerts_chat_id_is_required_when_alerts_are_enabled() -> None:
    with pytest.raises(ValidationError, match="RUNTIME_ALERTS_CHAT_ID"):
        BotSettingsWithoutDotenv(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
            RUNTIME_ALERTS_ENABLED=True,
        )


def test_runtime_alerts_chat_id_is_parsed_when_alerts_are_enabled() -> None:
    parsed_settings = BotSettingsWithoutDotenv(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
        RUNTIME_ALERTS_ENABLED=True,
        RUNTIME_ALERTS_CHAT_ID=987654321,
    )

    assert parsed_settings.runtime_alerts_enabled is True
    assert parsed_settings.runtime_alerts_chat_id == 987654321


def test_broadcast_allowed_roles_rejects_unknown_role(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROADCAST_ALLOWED_ROLES", "Admin,WrongRole")

    with pytest.raises(ValidationError, match="Unknown role"):
        BotSettingsWithoutDotenv(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
        )


def test_role_request_admin_tg_id_must_be_greater_than_zero() -> None:
    with pytest.raises(ValidationError, match="ROLE_REQUEST_ADMIN_TG_ID"):
        BotSettingsWithoutDotenv(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=0,
        )


def test_role_request_admin_tg_id_is_required() -> None:
    with pytest.raises(ValidationError) as exc_info:
        BotSettingsWithoutDotenv(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
        )

    assert any(
        error["loc"] == ("ROLE_REQUEST_ADMIN_TG_ID",) and error["type"] == "missing"
        for error in exc_info.value.errors()
    )
