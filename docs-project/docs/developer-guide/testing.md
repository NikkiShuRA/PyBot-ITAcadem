# Тестирование

Качество кода проверяется через `just quality-gate`.

## Основные команды

```bash
just format-check
just lint
just type-check
uv run pytest -q
just docs-build
```

## Что проверять при изменениях

- для сервисов, DTO и репозиториев: targeted unit/integration tests;
- для пользовательских bot-flow: поведение handler/dialog flow;
- для документации: строгую сборку MkDocs;
- для крупных изменений: дополнительный smoke-check критичного сценария.

## Полезное правило

Если модуль переименован или API изменился, сразу обновляйте страницу в `docs-project/docs/api-reference/`, иначе `mkdocstrings` начнет падать на отсутствующих импортах.
