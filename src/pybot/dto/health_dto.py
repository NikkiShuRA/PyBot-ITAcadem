"""DTO для проверки состояния (health checks) сервисов и приложения."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, Field

from .base_dto import BaseDTO


class HealthCheckDTO(BaseDTO):
    """Детали одиночной проверки готовности (readiness check).

    Args:
        name (str): Человекочитаемое название проверки (например, "database").
        status (str): Статус проверки ("ok" или "fail").
        details (str | None): Опциональные детали сбоя или дополнительная информация.
        latency_ms (int | None): Опциональное время выполнения проверки в миллисекундах.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "database",
                    "status": "ok",
                    "details": None,
                    "latency_ms": 8,
                }
            ]
        }
    )

    name: str = Field(
        description="Название проверки (например, database).",
        examples=["database"],
    )
    status: Literal["ok", "fail"] = Field(
        description="Статус проверки.",
        examples=["ok"],
    )
    details: str | None = Field(
        default=None,
        description="Дополнительные детали или текст ошибки.",
        examples=["db timeout"],
    )
    latency_ms: int | None = Field(
        default=None,
        ge=0,
        description="Время выполнения проверки в миллисекундах.",
        examples=[8],
    )


class HealthStatusDTO(BaseDTO):
    """Общий статус работоспособности / готовности приложения.

    Args:
        status (str): Сводный статус ("ok" или "fail").
        checks (list[HealthCheckDTO]): Список отдельных проверок (может быть пустым).
        timestamp (datetime): UTC-метка времени генерации статуса.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "ok",
                    "checks": [
                        {
                            "name": "database",
                            "status": "ok",
                            "details": None,
                            "latency_ms": 8,
                        }
                    ],
                    "timestamp": "2026-02-23T18:00:00Z",
                }
            ]
        }
    )

    status: Literal["ok", "fail"] = Field(
        description="Общий статус сервиса.",
        examples=["ok"],
    )
    checks: list[HealthCheckDTO] = Field(
        description="Список проверок готовности.",
        examples=[
            [
                {
                    "name": "database",
                    "status": "ok",
                    "details": None,
                    "latency_ms": 8,
                }
            ]
        ],
    )
    timestamp: datetime = Field(
        description="UTC-время формирования статуса.",
        examples=["2026-02-23T18:00:00Z"],
    )
