from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated

import pendulum
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic_extra_types.cron import CronStr
from pydantic_extra_types.timezone_name import TimeZoneName

from ..core.constants import LevelTypeEnum, TaskScheduleKind


class BaseValueModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Points(BaseValueModel):
    """
    Класс для представления количества очков.

    Attributes:
        value (int): Количество очков.
        point_type (Points_type_enum): Тип очков.

    Methods:
        adjust (int): Меняет количество очков на заданное значение.

    Returns:
        Points: Новый объект Points с измененным количеством очков.

    """

    value: Annotated[int, Field(strict=True, ge=-(2**31), le=2**31 - 1)]
    point_type: LevelTypeEnum

    def adjust(self, delta: int) -> Points:
        """
        Меняет количество очков на заданное значение.

        Args:
            delta (int): Заданное изменение количества очков.

        Returns:
            Points: Новый объект Points с измененным количеством очков.

        """

        new_value = self.value + delta
        return Points(value=new_value, point_type=self.point_type)

    def is_positive(self) -> bool:
        """Семантика: value > 0?"""
        return self.value > 0

    def is_negative(self) -> bool:
        """Семантика: value < 0?"""
        return self.value < 0

    def is_negative_delta(self, delta: int) -> bool:
        """Семантика: delta < 0?"""
        return delta < 0

    def compare_to_threshold(self, threshold: int) -> bool:
        """Семантика: value >= threshold?"""
        return self.value >= threshold

    def compare_to_past_threshold(self, threshold: int) -> bool:
        """Семантика: value < threshold?"""
        return self.value < threshold

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Points):
            return self.value == other.value and self.point_type == other.point_type
        return False

    def __hash__(self) -> int:
        return hash((self.value, self.point_type))

    def __str__(self) -> str:
        type_name = self.point_type.value.lower()
        return f"{self.value} {type_name}"

    def __repr__(self) -> str:
        return f"Points(value={self.value}, point_type={self.point_type})"

    def __ge__(self, other: Points | int) -> bool:
        val = other.value if isinstance(other, Points) else other
        return self.value >= val

    def __lt__(self, other: Points | int) -> bool:
        val = other.value if isinstance(other, Points) else other
        return self.value < val

    def __add__(self, other: Points | int) -> Points:
        if isinstance(other, int):
            return self.adjust(other)

        if isinstance(other, Points):
            if self.point_type != other.point_type:
                raise ValueError(f"Cannot add {other.point_type} to {self.point_type}")
            return self.adjust(other.value)

        raise NotImplementedError(f"Addition not supported between Points and {type(other)}")

    def __sub__(self, other: Points | int) -> Points:
        if isinstance(other, int):
            return self.adjust(-other)

        if isinstance(other, Points):
            if self.point_type != other.point_type:
                raise ValueError(f"Cannot subtract {other.point_type} from {self.point_type}")
            return self.adjust(-other.value)

        raise NotImplementedError(f"Subtraction not supported between Points and {type(other)}")


# TODO add domain errors
class TaskSchedule(BaseValueModel):
    model_config = ConfigDict(extra="forbid", frozen=True, arbitrary_types_allowed=True)

    kind: TaskScheduleKind
    run_at: pendulum.DateTime | None = None
    interval: timedelta | None = None
    cron: CronStr | None = None
    timezone: TimeZoneName | None = None

    @classmethod
    def immediate(cls) -> TaskSchedule:
        return cls(kind=TaskScheduleKind.IMMEDIATE)

    @classmethod
    def at(cls, run_at: datetime | pendulum.DateTime) -> TaskSchedule:
        return cls.model_validate({"kind": TaskScheduleKind.AT, "run_at": run_at})

    @classmethod
    def every(cls, interval: timedelta) -> TaskSchedule:
        return cls(kind=TaskScheduleKind.INTERVAL, interval=interval)

    @classmethod
    def cron_based(cls, cron: str, timezone: str = "UTC") -> TaskSchedule:
        return cls.model_validate({"kind": TaskScheduleKind.CRON, "cron": cron, "timezone": timezone})

    @field_validator("run_at", mode="before")
    @classmethod
    def validate_run_at(cls, value: object) -> pendulum.DateTime | None:
        if value is None:
            return None
        if isinstance(value, pendulum.DateTime):
            if value.tzinfo is None:
                raise ValueError("run_at must be timezone-aware")
            return value
        if isinstance(value, datetime):
            if value.tzinfo is None:
                raise ValueError("run_at must be timezone-aware")
            return pendulum.instance(value)

        raise ValueError("run_at must be a datetime or pendulum.DateTime instance")

    @field_validator("interval")
    @classmethod
    def validate_interval(cls, value: timedelta | None) -> timedelta | None:
        if value is None:
            return None
        if value <= timedelta(0):
            raise ValueError("interval must be greater than zero")
        if value.total_seconds() < 1:
            raise ValueError("interval must be at least 1 second")
        return value

    @model_validator(mode="after")
    def validate_shape(self) -> TaskSchedule:
        match self.kind:
            case TaskScheduleKind.IMMEDIATE:
                self._validate_immediate_schedule()
            case TaskScheduleKind.AT:
                self._validate_at_schedule()
            case TaskScheduleKind.INTERVAL:
                self._validate_interval_schedule()
            case TaskScheduleKind.CRON:
                self._validate_cron_schedule()

        return self

    def _validate_immediate_schedule(self) -> None:
        if any(value is not None for value in (self.run_at, self.interval, self.cron, self.timezone)):
            raise ValueError("immediate schedule must not contain timing fields")

    def _validate_at_schedule(self) -> None:
        if self.run_at is None:
            raise ValueError("at schedule requires run_at")
        if any(value is not None for value in (self.interval, self.cron, self.timezone)):
            raise ValueError("at schedule must contain only run_at")

    def _validate_interval_schedule(self) -> None:
        if self.interval is None:
            raise ValueError("interval schedule requires interval")
        if any(value is not None for value in (self.run_at, self.cron, self.timezone)):
            raise ValueError("interval schedule must contain only interval")

    def _validate_cron_schedule(self) -> None:
        if self.cron is None:
            raise ValueError("cron schedule requires cron expression")
        if self.run_at is not None or self.interval is not None:
            raise ValueError("cron schedule must not contain run_at or interval")
        if self.timezone is None:
            raise ValueError("cron schedule requires timezone")

    def as_taskiq_datetime(self) -> pendulum.DateTime:
        if self.run_at is None:
            raise ValueError("run_at is only available for AT schedules")
        return self.run_at
