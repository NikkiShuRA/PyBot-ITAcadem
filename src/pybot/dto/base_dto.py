"""Базовые классы для объектов передачи данных (DTO)."""

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """Базовый класс для всех объектов передачи данных (DTO).

    Запрещает использование незадекларированных полей и делает модели неизменяемыми.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True)
