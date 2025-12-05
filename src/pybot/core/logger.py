# src/pybot/core/logger.py
from __future__ import annotations

import sys

from loguru import Logger
from loguru import logger as loguru_logger

from .config import settings


def setup_logger() -> Logger:
    """Настройка и инициализация логгера."""
    loguru_logger.remove()

    # Основной формат для консоли
    loguru_logger.add(
        sys.stdout,
        level=settings.log_level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
        enqueue=True,
    )

    # Продакшен-логи (сериализованные ошибки)
    if not settings.debug:
        loguru_logger.add(
            sys.stdout,
            level=settings.log_level.upper(),
            format="{message}",
            serialize=True,
            enqueue=True,
            filter=lambda record: record["level"].no >= loguru_logger.level("WARNING").no,
        )

    return loguru_logger
