from collections.abc import Callable

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable


def role_filter(expected_role: str) -> Callable[[dict, Whenable, DialogManager], bool]:
    """Фильтр для Conditional UI для демонстраци виджетов aiogram-dialog в зависимости от роли."""

    def _filter(data: dict, widget: Whenable, manager: DialogManager) -> bool:
        user_roles = manager.middleware_data.get("user_roles", ())
        return expected_role in user_roles

    return _filter
