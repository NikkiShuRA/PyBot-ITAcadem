from sqlalchemy import Sequence

from ...core import logger
from ...db.models import Level


class LevelCalculator:
    """Сервис для расчета текущего уровня пользователя на основе накопленных баллов."""

    def calculate_level(self, current_points: int, all_levels: Sequence[Level]) -> Level | None:
        """Определяет подходящий уровень исходя из количества баллов.

        Args:
            current_points: Текущее количество баллов пользователя.
            all_levels: Список всех доступных уровней.

        Returns:
            Level | None: Объект уровня или None, если подходящий уровень не найден.
        """
        # Сортируем уровни по возрастанию требований (на всякий случай)
        sorted_levels = sorted(all_levels, key=lambda level: level.required_points)

        # Ищем самый высокий уровень, который покрывают наши баллы
        current_level = None
        for level in sorted_levels:
            if current_points >= level.required_points:
                current_level = level
            else:
                # Как только требований стало больше, чем у нас баллов — стоп
                break

        if current_level:
            return current_level
        else:
            logger.warning("No level found for current points: %d", current_points)
            return None
