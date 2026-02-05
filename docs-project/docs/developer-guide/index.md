# 🛠 Developer Guide

Информация для разработчиков, которые хотят контрибьютить в проект.

## Примечание по архитектуре

Проект построен на **Clean Architecture**:

```
src/
├── domain/       # Pure business logic
├── services/     # Use cases
├── infrastructure/  # Repos, external APIs
└── handlers/     # Telegram handlers
```

## Разделы

- [Архитектура проекта](architecture.md)
- [Как контрибьютить](contributing.md)
- [Тестирование](testing.md)
- [Деплой](deployment.md)

## Быстрая подготовка окружения

```bash
git clone <repo>
cd PyBot_ITAcadem
uv sync
pre-commit install
make test
```
