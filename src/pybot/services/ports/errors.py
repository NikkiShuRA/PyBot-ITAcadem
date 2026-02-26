from dataclasses import dataclass


class NotificationError(Exception):
    """Base notification delivery error."""


@dataclass(slots=True)
class NotificationTemporaryError(NotificationError):
    """Temporary notification delivery error that may be retried."""

    message: str
    retry_after_seconds: float | None = None

    def __str__(self) -> str:
        return self.message


@dataclass(slots=True)
class NotificationPermanentError(NotificationError):
    """Permanent notification delivery error that should not be retried."""

    message: str

    def __str__(self) -> str:
        return self.message
