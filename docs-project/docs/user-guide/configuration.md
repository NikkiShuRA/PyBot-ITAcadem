# Конфигурация

Настройки приложения определены в [`pybot.core.config.BotSettings`](../api-reference/core.md). Источником значений служит `.env`.

## Обязательные переменные

| Переменная | Назначение |
| --- | --- |
| `BOT_TOKEN` | production-токен бота |
| `BOT_TOKEN_TEST` | тестовый токен |
| `BOT_MODE` | режим `test` или `prod` |
| `ROLE_REQUEST_ADMIN_TG_ID` | Telegram ID администратора для role request |
| `DATABASE_URL` | строка подключения к SQLite |

## Часто используемые параметры

| Переменная | Что регулирует |
| --- | --- |
| `LOG_LEVEL` | уровень логирования |
| `DEBUG` | debug-режим |
| `FSM_STORAGE_BACKEND` | backend хранения FSM |
| `REDIS_URL` | Redis для FSM и TaskIQ |
| `NOTIFICATION_BACKEND` | `telegram` или `logging` |
| `TELEGRAM_PROXY_URL` | optional proxy для Telegram Bot API |
| `RUNTIME_ALERTS_ENABLED` | включает runtime alerts для bot startup/shutdown |
| `RUNTIME_ALERTS_CHAT_ID` | chat id для runtime alerts |
| `HEALTH_API_ENABLED` | отдельный health API |

## Broadcast-настройки

В `BotSettings` также есть группа параметров для рассылок:

- `BROADCAST_BULK_SIZE`
- `BROADCAST_MAX_CONCURRENCY`
- `BROADCAST_BATCH_PAUSE_MS`
- `BROADCAST_JITTER_MIN_MS`
- `BROADCAST_JITTER_MAX_MS`
- `BROADCAST_RETRY_ATTEMPTS`
- `BROADCAST_RETRY_MAX_WAIT_S`

!!! tip "Практика"
    Для локальной разработки удобнее держать `BOT_MODE=test`, `FSM_STORAGE_BACKEND=memory` и SQLite в каталоге проекта.

`TELEGRAM_PROXY_URL` можно оставить пустым. Переменная нужна только для окружений, где доступ к Telegram Bot API возможен через proxy.

`RUNTIME_ALERTS_ENABLED` и `RUNTIME_ALERTS_CHAT_ID` тоже являются опциональными. В v1 они покрывают только lifecycle основного `bot` runtime: startup-уведомление идет через TaskIQ, а shutdown-уведомление отправляется напрямую как best effort.
