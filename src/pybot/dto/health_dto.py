from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, Field

from .base_dto import BaseDTO


class HealthCheckDTO(BaseDTO):
    """Single readiness check details.

    Args:
        name: Human-readable name of the check (e.g. "database").
        status: Check status ("ok" or "fail").
        details: Optional failure or extra details.
        latency_ms: Optional check latency in milliseconds.
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
    """Overall health/readiness status.

    Args:
        status: Summary status ("ok" or "fail").
        checks: List of individual checks (may be empty).
        timestamp: UTC timestamp when the status was produced.
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
