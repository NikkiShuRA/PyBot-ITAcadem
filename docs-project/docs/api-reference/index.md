# Справочник API

Автогенерируемая документация строится через `mkdocstrings` и должна ссылаться только на реально существующие модули.

## Разделы

- [Core](core.md) — конфигурация, константы, логирование, bootstrap.
- [Services](services.md) — application layer и use cases.
- [Domain](domain.md) — domain exceptions и domain services.
- [Infrastructure](infrastructure.md) — repositories, adapters, TaskIQ integration.
- [DTO](dto.md) — Pydantic DTO и value objects.

## Правило сопровождения

Если модуль перенесен, переименован или удален, API-страницы нужно обновлять в том же изменении. Иначе строгая сборка документации начнет падать на импортах.
