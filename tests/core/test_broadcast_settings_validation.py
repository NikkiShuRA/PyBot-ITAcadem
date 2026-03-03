import pytest
from pydantic import ValidationError
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from pybot.core.config import BotSettings

ADMIN_TG_ID = 123_456_789


def test_broadcast_jitter_range_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_JITTER_MAX_MS"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
            BROADCAST_JITTER_MIN_MS=200,
            BROADCAST_JITTER_MAX_MS=100,
        )


def test_broadcast_bulk_size_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_BULK_SIZE"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
            BROADCAST_BULK_SIZE=0,
        )


def test_broadcast_batch_pause_min_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_BATCH_PAUSE_MS"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
            BROADCAST_BATCH_PAUSE_MS=600,
        )


def test_broadcast_max_text_length_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_MAX_TEXT_LENGTH"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
            BROADCAST_MAX_TEXT_LENGTH=0,
        )


def test_auto_admin_telegram_ids_parsed_from_json_array(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTO_ADMIN_TELEGRAM_IDS", "[123456789,987654321,123456789]")

    parsed_settings = BotSettings(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
    )

    assert parsed_settings.auto_admin_telegram_ids == {123456789, 987654321}


def test_broadcast_allowed_roles_parsed_from_comma_separated_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROADCAST_ALLOWED_ROLES", "Admin,Mentor,Admin")

    parsed_settings = BotSettings(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
    )

    assert parsed_settings.broadcast_allowed_roles == {"Admin", "Mentor"}


def test_broadcast_allowed_roles_default_is_admin() -> None:
    parsed_settings = BotSettings(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
    )

    assert parsed_settings.broadcast_allowed_roles == {"Admin"}


def test_broadcast_allowed_roles_rejects_unknown_role(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROADCAST_ALLOWED_ROLES", "Admin,WrongRole")

    with pytest.raises(ValidationError, match="Unknown role"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=ADMIN_TG_ID,
        )


def test_role_request_admin_tg_id_must_be_greater_than_zero() -> None:
    with pytest.raises(ValidationError, match="ROLE_REQUEST_ADMIN_TG_ID"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ROLE_REQUEST_ADMIN_TG_ID=0,
        )


def test_role_request_admin_tg_id_is_required() -> None:
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
            return (init_settings,)

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
