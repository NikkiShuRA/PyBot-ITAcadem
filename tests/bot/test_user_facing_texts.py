from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TARGET_FILES = [
    PROJECT_ROOT / "src/pybot/presentation/texts/texts.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/dialogs/user_reg/handlers.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/dialogs/user_reg/windows.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/handlers/common/start.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/handlers/common/misc.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/handlers/common/dialog_errors.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/handlers/broadcast/broadcast_commands.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/handlers/points/grand_points.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/handlers/roles/change_roles.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/handlers/roles/change_competences.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/handlers/roles/role_catalog.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/handlers/roles/show_roles.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/handlers/roles/role_request_flow.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/keyboards/auth.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/keyboards/role_request_keyboard.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/middlewares/role.py",
    PROJECT_ROOT / "src/pybot/presentation/bot/utils/text_id_searches.py",
    PROJECT_ROOT / "src/pybot/services/user_services/user_profile.py",
    PROJECT_ROOT / "src/pybot/services/role_request.py",
    PROJECT_ROOT / "src/pybot/infrastructure/ports/telegram_notification_service.py",
]
BROKEN_MARKERS = ("Рџ", "Рќ", "СЃ", "С‚", "вЂ", "пё", "�")


@pytest.mark.parametrize("file_path", TARGET_FILES)
def test_user_facing_files_do_not_contain_mojibake(file_path: Path) -> None:
    content = file_path.read_text(encoding="utf-8")
    assert not any(marker in content for marker in BROKEN_MARKERS), file_path.as_posix()
