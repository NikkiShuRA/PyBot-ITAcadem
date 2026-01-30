# ADR 005: Использование Aiogram Middleware совместно с Dishka DI для Cross-Cutting Concerns

## Дата: 30-01-2026

## Статус: Accepted

## Контекст

В проекте требуется централизованная предобработка входящих обновлений от Telegram (логирование, rate-limiting, проверка ролей, потенциально обновление статуса активности пользователя).

При этом мы придерживаемся принципа **Thin Handlers** (ARCHITECTURE.md): хендлеры должны оставаться максимально простыми и не содержать инфраструктурную или кросс-катинговую логику.

Мы уже используем **Dishka** как DI-контейнер и хотим сохранить единообразный способ внедрения зависимостей (AsyncSession, Repository, Service) во всех местах.

## Решение

Принято решение использовать **Aiogram Middleware** в сочетании с **Dishka DI** для реализации cross-cutting concerns.

Принято решение использовать **[Aiogram Middleware + Dishka DI]**.

### Детали реализации

1. Middleware регистрируются на уровне `Dispatcher` (update, message, callback_query и т.д.).
2. Через `dishka.integrations.aiogram` и `setup_dishka(..., auto_inject=True)` middleware получают доступ к scoped зависимостям.
3. Внутри `__call__` middleware извлекают зависимости через `async with container() as c: db = await c.get(AsyncSession); repo = await c.get(UserRepository)`.
4. Реализованы:
   - `LoggerMiddleware` — логирует минимальную информацию о событии
   - `RateLimitMiddleware` — проверяет флаг `rate_limit` через `get_flag` и применяет `AsyncLimiter`
   - `RoleMiddleware` — проверяет флаг `role` и вызывает `repo.has_role(telegram_id, role_name)`
5. User Activity Status **не** реализуется в middleware (см. альтернативы).

Пример RoleMiddleware:

```python
async def __call__(self, handler, event, data):
    required_role = get_flag(data, "role")
    if not required_role:
        return await handler(event, data)

    container = data.get(CONTAINER_NAME)
    async with container() as c:
        db = await c.get(AsyncSession)
        repo = await c.get(UserRepository)
        has_permission = await repo.has_role(db=db, telegram_id=user.id, role_name=required_role)
```

## Альтернативы

### Декораторы на каждом хендлере (@requires_role("Admin"))

Плюсы: явно видно требования в коде хендлера.
Минусы: дублирование, нарушение Thin Handlers, сложнее централизованное управление.

### Вызов сервисов внутри каждого хендлера

Плюсы: вся логика в Application слое.
Минусы: сильное дублирование кода, риск забыть проверку, handlers перестают быть тонкими.

### Встроенные механизмы Aiogram (например, встроенный rate-limiter)

Плюсы: меньше кода.
Минусы: ограниченная гибкость, нет интеграции с Dishka и нашими репозиториями.

## Последствия

### Положительные

[+] Централизация cross-cutting logic → легко добавлять/изменять поведение для всех событий.
[+] Сохранение Thin Handlers и соответствие ARCHITECTURE.md.
[+] Единообразное внедрение зависимостей через Dishka → scoped сессии, тестируемость.
[+] Fail-fast: проверка ролей и rate-limit происходит до выполнения бизнес-логики.

### Отрицательные

[-] Middleware могут стать сложными при росте проекта (риск God Middleware).
[-] Сложнее отлаживать (логика распределена между middleware и хендлерами).
[-] Тестирование middleware требует mock-контейнера Dishka.

## Ссылки

ARCHITECTURE.md — Presentation Layer и Thin Handlers
Aiogram Middleware documentation
Dishka Aiogram integration
ADR-001 (DTO & Domain), ADR-002 (Immutability), ADR-003 (Value Objects)
