# PyBot ITAcadem 🚀

Привет! Мы разрабатываем этот Telegram‑бот для ITAcadem StartUP.
Цель проекта — дать участникам простой вход в экосистему академии: авторизация по номеру телефона, создание профиля и в дальнейшем работа с задачами, проектами и достижениями.

---

## О чём этот бот 🤖

Цель проекта — создать удобную точку входа в экосистему академии: авторизация через Telegram, управление профилем, геймификация через баллы и уровни, и в будущем — работа с задачами и проектами.

---

## Что умеет бот сейчас ✅

### Авторизация и профиль

/start в личке:
Если пользователь уже зарегистрирован — показывает профиль с прогресс-баром уровней
Если нет — запускает диалог регистрации через номер телефона

- /profile — детальный просмотр профиля с:
  - Академическим и репутационным уровнями
  - Прогресс-баром до следующего уровня
  - Текущим количеством баллов

### Геймификация (админ-команды)

- /academic_points @user 100 "за решение задачи" — начисление академических баллов
- /reputation_points @user 50 "за помощь коллегам" — начисление репутационных баллов
Автоматическое повышение/понижение уровня при изменении баллов

### Система ролей

Поддержка ролей: Student, Mentor, Admin
Проверка прав через middleware (флаг role="Admin" на хендлерах)

### Инфраструктурные фичи

/ping — health-check с проверкой роли
/info — информация о проекте и ссылка на репозиторий
/help — справка по доступным командам

---

## Стек технологий 🛠

## Ядро

- Python 3.12+ с асинхронным программированием (asyncio)
- aiogram 3.22+ — современный фреймворк для Telegram-ботов
- aiogram-dialog 2.4+ — управление многошаговыми диалогами
- База данных
- SQLite (основная БД для разработки и продакшена)
- SQLAlchemy 2.0 Async — ORM с поддержкой асинхронных операций
- Alembic — миграции схемы БД
- Rich ORM Models — бизнес-логика инкапсулирована в моделях (User.add_role(), User.set_initial_levels())

## Архитектура

- Dishka — внедрение зависимостей (DI-контейнер)
- Repository Pattern — слой абстракции над БД (UserRepository, LevelRepository)
- Middleware — кросс-катинговые задачи:
  - RoleMiddleware — проверка прав доступа
  - RateLimitMiddleware — защита от спама (3 уровня: cheap/moderate/expensive)
  - UserActivityMiddleware — отслеживание активности пользователей
  - LoggerMiddleware — структурированное логирование событий
- Value Objects — семантические типы (Points для баллов)
- DTO — валидация и сериализация данных на границах слоёв

### Вспомогательные инструменты

- loguru — логирование с поддержкой структурированных логов
- tyro — CLI для скриптов, используется в `fill_point_db.py`
- Faker — генерация тестовых данных
- phonenumbers — валидация и нормализация телефонных номеров
- uv — современный менеджер пакетов и зависимостей

---

## Структура проекта 🌳

Ниже упрощённое дерево, чтобы было понятно, где что лежит:

```plain text
PyBot_ITAcadem/
├── src/
│   └── pybot/
│       ├── bot/                         # Presentation layer: aiogram routers, dialogs, UI text
│       │   ├── dialogs/                 # aiogram-dialog сценарии и окна
│       │   ├── filters/                 # Telegram-specific filters and router factories
│       │   ├── handlers/                # Thin handlers grouped by feature
│       │   │   ├── broadcast/
│       │   │   ├── common/
│       │   │   ├── points/
│       │   │   ├── profile/
│       │   │   └── roles/
│       │   ├── keyboards/               # Reply and inline keyboards
│       │   ├── middlewares/             # Cross-cutting middleware
│       │   ├── utils/                   # Bot-only helper functions
│       │   ├── texts.py                 # Shared user-facing text constants
│       │   └── tg_bot_run.py            # Telegram bot bootstrap
│       ├── core/                        # Settings, enums, shared logger setup
│       ├── db/                          # Database setup and rich ORM models
│       │   ├── models/
│       │   │   ├── level_module/
│       │   │   ├── role_module/
│       │   │   ├── task_module/
│       │   │   └── user_module/
│       │   ├── base_class.py
│       │   └── database.py
│       ├── di/                          # Dishka composition root and providers
│       │   └── containers.py
│       ├── domain/                      # Domain rules that do not belong to ORM or transport layers
│       │   ├── exceptions.py
│       │   └── services/
│       ├── dto/                         # DTOs and value objects at layer boundaries
│       │   ├── *_dto.py
│       │   └── value_objects.py
│       ├── health/                      # Health/readiness API and server wiring
│       ├── infrastructure/              # Repositories, adapters, and external integrations
│       │   ├── ports/                   # Concrete notification adapters
│       │   ├── roles/                   # Role-related repositories
│       │   └── taskiq/                  # Background jobs and scheduling integration
│       ├── mappers/                     # Mapping helpers between transport/dialog data and DTOs
│       ├── services/                    # Application layer orchestration
│       │   ├── ports/                   # Service-level ports and contracts
│       │   └── user_services/           # User-facing service specializations
│       └── utils/                       # Shared project utilities
├── fill_point_db.py                # CLI-скрипт для наполнения БД тестовыми данными
├── db_reset_start.py               # Сброс БД + миграции + заполнение + запуск бота
├── run.py                          # Запуск бота
├── AGENTS.md                       # Operating contract for AI agents
├── ARCHITECTURE.md                 # Архитектурный манифест и инварианты
└── alembic/                        # Миграции БД

```

---

## Как запустить локально 💻

1. Клонировать репозиторий:

   ```bash
   git clone https://github.com/NikkiShuRA/PyBot-ITAcadem.git
   cd PyBot-ITAcadem
   ```

2. Создать и активировать виртуальное окружение:

   Создание:

   ```bash
   python -m venv .venv
   ```

   Активация:

   ```bash
   # bash
   source .venv/bin/activate
   ```

3. Установить зависимости:

   ```bash
   uv sync
   ```

   Если хотите без dev-зависимостей:

   ```bash
   uv sync --no-dev
   ```

4. Создать `.env` в корне проекта:

   ```plain text
   # Production токен (если используете)
   BOT_TOKEN=your_production_bot_token_here

   # Тестовый токен (используется в `config.py` как BOT_TOKEN)
   BOT_TOKEN_TEST=your_test_bot_token_here

   # SQLite connection
   DATABASE_URL=sqlite+aiosqlite:///./your_name.db

   DEBUG=True
   LOG_LEVEL=INFO
   ```

5. Запустить скрипт автозаполнения БД:

   ```bash
   python fill_point_db.py

   # Показать CLI-параметры seed-скрипта
   python fill_point_db.py --help

   # Непосредственно запустить только нужные этапы
   python fill_point_db.py --skip-levels --skip-roles --skip-competencies --num-fake-users 10
   ```

6. Запустить бота:

   ```bash
   python run.py
   ```

---

## 📚 Документация

ARCHITECTURE.md — принципы проектирования и архитектурные ограничения
ADR (Architecture Decision Records) — решения по ключевым архитектурным вопросам:

- 001 — Введение DTO и доменных сущностей
- 002 — Иммутабельность DTO
- 003 — Value Objects (паттерн Points)
- 004 — Миграция с PostgreSQL на SQLite
- 005 — Middleware + Dishka DI
- 006 — Внедрение репозиториев и сервисов
- 007 - Замена Domain entities на Rich ORM Models

---

## Куда всё движется дальше 📈

То, что сейчас есть — это онбординг и фундамент.
Дальше планируем:

- завязать на бота задачи (выдача, решения, статусы);
- добавить геймификацию: уровни, компетенции, достижения, баллы;
- расширить роли (студент, ментор, админ) и дать им разные возможности прямо в Telegram.

Если хочешь что‑то предложить или помочь с разработкой — форкай, открывай PR или заводи issue 🙂

---

## Health API

Минимальные эндпоинты наблюдаемости запускаются в отдельном процессе.

В `.env`:

```bash
HEALTH_API_ENABLED=True
HEALTH_API_HOST=0.0.0.0
HEALTH_API_PORT=8001
```

Эндпоинты:

- `GET /health` — liveness
- `GET /ready` — readiness (проверка БД)

---

## Runbook

### Deploy

1. Prepare release:
   - pull code (`git pull`) or checkout target tag/commit;
   - verify `.env` values (`BOT_TOKEN`, `DATABASE_URL`, health API settings);
   - run `just quality-gate`.
2. Prepare data:
   - create DB backup (for SQLite: copy `.db` file before release);
   - confirm migrations are up to date.
3. Roll out:
   - apply migrations: `uv run alembic upgrade head`;
   - restart app:
     - systemd/local: restart service;
     - Docker: `docker compose up -d --build`.
4. Verify startup logs:
   - no DI/DB/Bot initialization errors;
   - polling is running.

### Smoke-check

1. Check health endpoints:
   - `GET /health` returns 200;
   - `GET /ready` returns 200.
2. Check Telegram bot basics:
   - `/start` opens expected flow;
   - `/ping` returns expected response;
   - `/profile` works without errors.
3. Check logs:
   - no traceback in middlewares/handlers;
   - no DB connection/session close errors.

### Rollback

1. Stop current release or switch traffic away.
2. Checkout previous stable tag/commit.
3. Restore DB from backup if release included incompatible migrations/data changes.
4. Restart application on previous version.
5. Repeat smoke-check and confirm normal operation.
