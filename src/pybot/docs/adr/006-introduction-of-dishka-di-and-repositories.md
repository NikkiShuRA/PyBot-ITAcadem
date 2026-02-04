# ADR 006: Введение Dishka DI и паттерна Repository

## Дата: 01-02-2026

## Статус: Accepted

## Контекст

Ранее в проекте сессии БД (AsyncSession) передавались напрямую в хендлеры и middleware через глобальный `DbSessionMiddleware`. Это приводило к нескольким серьёзным проблемам:

- Lazy loading в моделях вызывал ошибку **MissingGreenlet** в async-контексте.
- Дублирование кода создания/обновления пользователей (create_user_profile, update_user_points_by_id).
- Хендлеры нарушали принцип **Thin Handlers** — содержали бизнес-логику, запросы к БД и маппинг.
- Отсутствие единого способа внедрения зависимостей (репозитории, сервисы, сессии).
- Трудности с тестированием и поддержкой scoped жизненного цикла сессий.
- Middleware (role, rate-limit, user_activity) не могли удобно получать репозитории и сервисы.

## Решение

Принято решение использовать **Dishka** как DI-контейнер и внедрить **паттерн Repository** для отделения доступа к данным от бизнес-логики.

Принято решение использовать **Dishka DI + Repository pattern**.

### Детали реализации

1. **Dishka контейнер** (`di/containers.py`):
   - `DatabaseProvider` — Engine (Scope.APP)
   - `SessionProvider` — новая AsyncSession на каждый запрос (Scope.REQUEST)
   - `RepositoryProvider` — stateless репозитории (Scope.APP)
   - `ServiceProvider` — сервисы с репозиториями (Scope.REQUEST)
   - `setup_dishka(..., auto_inject=True)` + `AiogramProvider`

2. **Repository layer** (`infrastructure/`):
   - `UserRepository`, `LevelRepository`, `ValuationRepository` — stateless, сессия передаётся в каждый метод
   - `get_by_telegram_id` с `selectinload(User.roles)` — решена проблема MissingGreenlet
   - `has_role`, `update_user_last_active` и др.

3. **Service layer** (`services/users.py`, `points.py`):
   - `UserService` получает репозитории в конструкторе
   - Бизнес-логика (register_student, set_user_role, track_activity) перенесена из хендлеров

4. **Middleware**:
   - `RoleMiddleware`, `RateLimitMiddleware`, `UserActivityMiddleware` получают зависимости через `async with container()`
   - `UserActivityMiddleware` работает как триггер: после хендлера вызывает `user_service.track_activity`

5. **Хендлеры** стали максимально тонкими: только парсинг + вызов сервиса.

## Альтернативы

- **Глобальная сессия / DbSessionMiddleware без DI**:
  - Плюсы: проще на старте
  - Минусы: MissingGreenlet, дублирование, нарушение Thin Handlers, сложнее тестирование

- **Декораторы на хендлерах (@requires_role, @inject)**:
  - Плюсы: явно видно требования
  - Минусы: дублирование, нарушение Thin Handlers, сложнее централизованное управление

- **Прямой доступ к БД в хендлерах**:
  - Плюсы: минимум кода
  - Минусы: сильное нарушение чистой архитектуры, плохая тестability, дублирование

## Последствия

### Положительные

- [+] Устранена ошибка MissingGreenlet
- [+] Хендлеры стали тонкими и соответствуют ARCHITECTURE.md
- [+] Scoped сессии на каждый update — правильный жизненный цикл
- [+] Легко тестировать сервисы и репозитории изолированно
- [+] Единообразное внедрение зависимостей во всех middleware и хендлерах
- [+] Логика активности пользователя вынесена в сервис, middleware — только триггер

### Отрицательные

- [-] Добавился boilerplate-код (контейнер, репозитории, мапперы)
- [-] Middleware стали чуть сложнее из-за scoped контейнера
- [-] Требуется аккуратное управление порядком include_routers и фильтров

## Ссылки

- ARCHITECTURE.md — Layered Architecture, Thin Handlers, Pragmatic DDD
- ADR-001 (DTO и Domain), ADR-002 (Immutability), ADR-003 (Value Objects), ADR-005 (Aiogram Middleware)
- Dishka documentation: <https://dishka.readthedocs.io/>
- Repository pattern (Martin Fowler)
