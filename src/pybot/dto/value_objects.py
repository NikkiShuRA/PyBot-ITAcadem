from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated

import pendulum
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic_extra_types.cron import CronStr
from pydantic_extra_types.timezone_name import TimeZoneName

from ..core.constants import PointsTypeEnum, TaskScheduleKind
from ..domain.exceptions import (
    TaskScheduleFieldTypeError,
    TaskScheduleFieldUnavailableError,
    TaskScheduleIntervalNonPositiveError,
    TaskScheduleIntervalTooShortError,
    TaskScheduleMissingFieldError,
    TaskScheduleTimezoneAwareRequiredError,
    TaskScheduleUnexpectedFieldsError,
)


class BaseValueModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Points(BaseValueModel):
    """Класс для представления количества очков.

    Attributes:
        value (int): Количество очков.
        point_type (PointsTypeEnum): Тип очков.

    Methods:
        adjust (int): Меняет количество очков на заданное значение.

    Returns:
        Points: Новый объект Points с измененным количеством очков.

    """

    value: Annotated[int, Field(strict=True, ge=-(2**31), le=2**31 - 1)]
    point_type: PointsTypeEnum

    def adjust(self, delta: int) -> Points:
        """Меняет количество очков на заданное значение.

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
                raise TaskScheduleTimezoneAwareRequiredError("run_at")
            return value
        if isinstance(value, datetime):
            if value.tzinfo is None:
                raise TaskScheduleTimezoneAwareRequiredError("run_at")
            return pendulum.instance(value)

        raise TaskScheduleFieldTypeError("run_at", "a datetime or pendulum.DateTime instance", value)

    @field_validator("interval")
    @classmethod
    def validate_interval(cls, value: timedelta | None) -> timedelta | None:
        if value is None:
            return None
        if value <= timedelta(0):
            raise TaskScheduleIntervalNonPositiveError(value)
        if value.total_seconds() < 1:
            raise TaskScheduleIntervalTooShortError(value)
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
        unexpected_fields = self._collect_present_fields("run_at", "interval", "cron", "timezone")
        if unexpected_fields:
            raise TaskScheduleUnexpectedFieldsError(TaskScheduleKind.IMMEDIATE, unexpected_fields)

    def _validate_at_schedule(self) -> None:
        if self.run_at is None:
            raise TaskScheduleMissingFieldError(TaskScheduleKind.AT, "run_at")
        unexpected_fields = self._collect_present_fields("interval", "cron", "timezone")
        if unexpected_fields:
            raise TaskScheduleUnexpectedFieldsError(TaskScheduleKind.AT, unexpected_fields)

    def _validate_interval_schedule(self) -> None:
        if self.interval is None:
            raise TaskScheduleMissingFieldError(TaskScheduleKind.INTERVAL, "interval")
        unexpected_fields = self._collect_present_fields("run_at", "cron", "timezone")
        if unexpected_fields:
            raise TaskScheduleUnexpectedFieldsError(TaskScheduleKind.INTERVAL, unexpected_fields)

    def _validate_cron_schedule(self) -> None:
        if self.cron is None:
            raise TaskScheduleMissingFieldError(TaskScheduleKind.CRON, "cron")
        unexpected_fields = self._collect_present_fields("run_at", "interval")
        if unexpected_fields:
            raise TaskScheduleUnexpectedFieldsError(TaskScheduleKind.CRON, unexpected_fields)
        if self.timezone is None:
            raise TaskScheduleMissingFieldError(TaskScheduleKind.CRON, "timezone")

    def _collect_present_fields(self, *field_names: str) -> tuple[str, ...]:
        return tuple(field_name for field_name in field_names if getattr(self, field_name) is not None)

    def as_taskiq_datetime(self) -> pendulum.DateTime:
        if self.run_at is None:
            raise TaskScheduleFieldUnavailableError("run_at", TaskScheduleKind.AT, self.kind)
        return self.run_at

    def as_interval(self) -> timedelta:
        if self.interval is None:
            raise TaskScheduleFieldUnavailableError("interval", TaskScheduleKind.INTERVAL, self.kind)
        return self.interval

    def as_cron_expression(self) -> str:
        if self.cron is None:
            raise TaskScheduleFieldUnavailableError("cron", TaskScheduleKind.CRON, self.kind)
        return str(self.cron)

    def as_timezone_name(self) -> str:
        if self.timezone is None:
            raise TaskScheduleFieldUnavailableError("timezone", TaskScheduleKind.CRON, self.kind)
        return str(self.timezone)
