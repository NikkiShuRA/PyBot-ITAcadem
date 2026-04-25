from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User

from pybot.presentation.bot import cmd_chat_id


def _build_message(*, chat_id: int, text: str = "/chat_id", from_user_id: int = 740_001) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Admin")
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=chat_id, type="supergroup"),
        from_user=sender,
        text=text,
    )


@pytest.mark.asyncio
async def test_cmd_chat_id_returns_current_chat_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(chat_id=-100_123_456_7890)
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await cmd_chat_id(message)

    answer_mock.assert_awaited_once_with("chat.id: -1001234567890")
