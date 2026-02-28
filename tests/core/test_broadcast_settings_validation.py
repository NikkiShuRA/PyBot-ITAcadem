import pytest
from pydantic import ValidationError

from pybot.core.config import BotSettings


def test_broadcast_jitter_range_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_JITTER_MAX_MS"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            BROADCAST_JITTER_MIN_MS=200,
            BROADCAST_JITTER_MAX_MS=100,
        )


def test_broadcast_bulk_size_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_BULK_SIZE"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            BROADCAST_BULK_SIZE=0,
        )


def test_broadcast_batch_pause_min_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_BATCH_PAUSE_MS"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            BROADCAST_BATCH_PAUSE_MS=600,
        )


def test_broadcast_max_text_length_validation() -> None:
    with pytest.raises(ValidationError, match="BROADCAST_MAX_TEXT_LENGTH"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            BROADCAST_MAX_TEXT_LENGTH=0,
        )


def test_auto_admin_telegram_ids_parsed_from_json_array(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTO_ADMIN_TELEGRAM_IDS", "[123456789,987654321,123456789]")

    parsed_settings = BotSettings(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
    )

    assert parsed_settings.auto_admin_telegram_ids == {123456789, 987654321}


def test_broadcast_allowed_roles_parsed_from_comma_separated_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROADCAST_ALLOWED_ROLES", "Admin,Mentor,Admin")

    parsed_settings = BotSettings(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
    )

    assert parsed_settings.broadcast_allowed_roles == {"Admin", "Mentor"}


def test_broadcast_allowed_roles_default_is_admin() -> None:
    parsed_settings = BotSettings(
        BOT_TOKEN="123456:prod",
        BOT_TOKEN_TEST="123456:test",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
    )

    assert parsed_settings.broadcast_allowed_roles == {"Admin"}


def test_broadcast_allowed_roles_rejects_unknown_role(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROADCAST_ALLOWED_ROLES", "Admin,WrongRole")

    with pytest.raises(ValidationError, match="Unknown role"):
        BotSettings(
            BOT_TOKEN="123456:prod",
            BOT_TOKEN_TEST="123456:test",
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
        )
