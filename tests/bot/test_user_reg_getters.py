from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast

import pytest
from aiogram_dialog import DialogManager

from pybot.presentation.bot import get_registration_competencies


@dataclass(slots=True)
class StubDialogManager:
    dialog_data: dict[str, object] = field(default_factory=dict)


@pytest.mark.asyncio
async def test_get_registration_competencies_returns_options_from_dialog_data() -> None:
    manager = StubDialogManager(
        dialog_data={
            "registration_competencies": [
                (1, "Python"),
                (2, "SQL"),
            ]
        }
    )

    result = await get_registration_competencies(cast(DialogManager, manager))

    assert result == {
        "registration_competencies": [
            (1, "Python"),
            (2, "SQL"),
        ]
    }


@pytest.mark.asyncio
async def test_get_registration_competencies_filters_invalid_entries() -> None:
    manager = StubDialogManager(
        dialog_data={
            "registration_competencies": [
                (1, "Python"),
                ("2", "SQL"),
                (3, 100),
                ("broken",),
            ]
        }
    )

    result = await get_registration_competencies(cast(DialogManager, manager))

    assert result == {"registration_competencies": [(1, "Python")]}
