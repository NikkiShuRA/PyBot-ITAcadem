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
