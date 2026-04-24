from datetime import date

from pybot.presentation.texts import render_profile_message
from pybot.core.constants import PointsTypeEnum
from pybot.dto import CompetenceReadDTO, LevelReadDTO, ProfileViewDTO, UserLevelReadDTO, UserReadDTO
from pybot.dto.value_objects import Points


def test_render_profile_message_keeps_sections_and_actions_left_aligned() -> None:
    profile_view = ProfileViewDTO(
        user=UserReadDTO(
            id=1,
            first_name="Илья",
            last_name="Тестов",
            patronymic=None,
            telegram_id=123_456,
            academic_points=Points(value=0, point_type=PointsTypeEnum.ACADEMIC),
            reputation_points=Points(value=0, point_type=PointsTypeEnum.REPUTATION),
            join_date=date(2025, 1, 1),
        ),
        academic_progress=Points(value=0, point_type=PointsTypeEnum.ACADEMIC),
        academic_level=UserLevelReadDTO(
            current_level=LevelReadDTO(
                name="Уровень 1",
                required_points=Points(value=0, point_type=PointsTypeEnum.ACADEMIC),
            ),
            next_level=LevelReadDTO(
                name="Уровень 2",
                required_points=Points(value=100, point_type=PointsTypeEnum.ACADEMIC),
            ),
        ),
        academic_current_points=Points(value=0, point_type=PointsTypeEnum.ACADEMIC),
        academic_next_points=Points(value=100, point_type=PointsTypeEnum.ACADEMIC),
        reputation_progress=Points(value=0, point_type=PointsTypeEnum.REPUTATION),
        reputation_level=UserLevelReadDTO(
            current_level=LevelReadDTO(
                name="Уровень 1",
                required_points=Points(value=0, point_type=PointsTypeEnum.REPUTATION),
            ),
            next_level=LevelReadDTO(
                name="Уровень 2",
                required_points=Points(value=100, point_type=PointsTypeEnum.REPUTATION),
            ),
        ),
        reputation_current_points=Points(value=0, point_type=PointsTypeEnum.REPUTATION),
        reputation_next_points=Points(value=100, point_type=PointsTypeEnum.REPUTATION),
        roles_data=["Student", "Admin"],
        competences=[],
    )

    rendered = render_profile_message(profile_view)

    assert "👋 Здравствуйте, Илья!" in rendered
    assert "\n<b>📘 Академический уровень</b>\n" in rendered
    assert "\n<b>⭐ Репутационный уровень</b>\n" in rendered
    assert "\n<b>🎭 Роли</b>\n- Student\n- Admin\n" in rendered
    assert "\n<b>🧩 Компетенции</b>\nПока не указаны\n" in rendered
    assert "\nОбновить профиль: /profile\nПосмотреть команды: /help" in rendered
    assert "        📘 Академический уровень" not in rendered
    assert "        🎭 Роли" not in rendered
    assert "        Обновить профиль: /profile" not in rendered


def test_render_profile_message_formats_competence_names_as_html_bold() -> None:
    profile_view = ProfileViewDTO(
        user=UserReadDTO(
            id=1,
            first_name="Илья",
            last_name="Тестов",
            patronymic=None,
            telegram_id=123_456,
            academic_points=Points(value=0, point_type=PointsTypeEnum.ACADEMIC),
            reputation_points=Points(value=0, point_type=PointsTypeEnum.REPUTATION),
            join_date=date(2025, 1, 1),
        ),
        academic_progress=Points(value=0, point_type=PointsTypeEnum.ACADEMIC),
        academic_level=UserLevelReadDTO(
            current_level=LevelReadDTO(
                name="Уровень 1",
                required_points=Points(value=0, point_type=PointsTypeEnum.ACADEMIC),
            ),
            next_level=LevelReadDTO(
                name="Уровень 2",
                required_points=Points(value=100, point_type=PointsTypeEnum.ACADEMIC),
            ),
        ),
        academic_current_points=Points(value=0, point_type=PointsTypeEnum.ACADEMIC),
        academic_next_points=Points(value=100, point_type=PointsTypeEnum.ACADEMIC),
        reputation_progress=Points(value=0, point_type=PointsTypeEnum.REPUTATION),
        reputation_level=UserLevelReadDTO(
            current_level=LevelReadDTO(
                name="Уровень 1",
                required_points=Points(value=0, point_type=PointsTypeEnum.REPUTATION),
            ),
            next_level=LevelReadDTO(
                name="Уровень 2",
                required_points=Points(value=100, point_type=PointsTypeEnum.REPUTATION),
            ),
        ),
        reputation_current_points=Points(value=0, point_type=PointsTypeEnum.REPUTATION),
        reputation_next_points=Points(value=100, point_type=PointsTypeEnum.REPUTATION),
        roles_data=[],
        competences=[
            CompetenceReadDTO(
                id=1,
                name="Docker",
                description="Контейнеризация приложений",
            )
        ],
    )

    rendered = render_profile_message(profile_view)

    assert "<b>Docker</b>: Контейнеризация приложений." in rendered
