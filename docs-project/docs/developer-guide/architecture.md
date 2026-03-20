# Архитектура

Этот раздел опирается на `ARCHITECTURE.md`, `AGENTS.md` и ADR в `src/pybot/docs/adr/`.

## Архитектурный стиль

Проект следует Layered Architecture с элементами Pragmatic DDD:

- presentation: `src/pybot/bot/`
- services: `src/pybot/services/`
- infrastructure: `src/pybot/infrastructure/`
- db/models: `src/pybot/db/`
- dto/value objects: `src/pybot/dto/`
- DI: `src/pybot/di/`

## Инварианты

- handlers и dialogs остаются тонкими;
- orchestration живет в сервисах;
- repositories не коммитят транзакции скрыто;
- DTO и value objects используются на границах слоев;
- lookup-семантика должна соответствовать ADR `008-nullable-and-strict-lookup-separation.md`.

## Что важно для документации

API Reference должен отражать реальную структуру проекта. Если модуль переименован или перенесен, вместе с кодом нужно обновлять и `docs-project/docs/api-reference/`.
