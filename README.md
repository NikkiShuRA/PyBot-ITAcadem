# PyBot ITAcadem

Асинхронный Telegram-бот для ITAcadem на `Python 3.12`, `aiogram 3`, `Dishka`, `SQLAlchemy 2` и `Pydantic v2`.

Сейчас проект закрывает не абстрактный "будущий MVP", а вполне конкретный набор сценариев:

- регистрация пользователя через Telegram-диалог;
- просмотр профиля с ролями, компетенциями и прогрессом по баллам;
- role request flow с подтверждением или отклонением администратором;
- админские команды для ролей, компетенций, баллов и рассылок;
- health/readiness API;
- Docker/runtime-контур с `Redis` и `TaskIQ`;
- production deploy skeleton через `docker-compose.prod.yml`, GitHub Actions и Ansible.

## Что реально есть в проекте сейчас

### Пользовательские сценарии

- `/start` в личном чате:
  - показывает профиль, если пользователь уже зарегистрирован;
  - иначе запускает пошаговую регистрацию.
- Регистрация через `aiogram-dialog`:
  - запрос контакта;
  - имя;
  - фамилия;
  - отчество;
  - выбор компетенций с возможностью пропуска.
- `/profile` показывает:
  - академический уровень;
  - репутационный уровень;
  - баллы;
  - роли;
  - компетенции.
- `/help`, `/info`, `/ping` и `/competences` работают как пользовательские команды.
- `/showcompetences [@user|id|reply]` показывает компетенции конкретного пользователя.

### Админские сценарии

- `/academic_points @user <число> "причина"` и `/reputation_points @user <число> "причина"` меняют баллы пользователя.
- `/addrole` и `/removerole` управляют ролями `Student`, `Mentor`, `Admin`.
- `/addcompetence` и `/removecompetence` управляют компетенциями пользователя.
- `/broadcast @all <текст>` рассылает сообщение всем.
- `/broadcast <Role> <текст>` рассылает по роли.
- `/broadcast <Competence> <текст>` рассылает по компетенции.

### Role request flow

- `/role_request <Student|Mentor|Admin>` создаёт запрос на роль.
- Администратор получает уведомление с inline-кнопками одобрения и отклонения.
- Есть защита от повторных активных запросов и cooldown после отклонения.

### Инфраструктурные возможности

- Отдельный FastAPI health API:
  - `GET /health` для liveness;
  - `GET /ready` для readiness с проверкой БД.
- Поддержка `Redis`:
  - как backend для FSM;
  - как broker/schedule backend для `TaskIQ`.
- Выделенные runtime-процессы:
  - `bot`;
  - `taskiq-worker`;
  - `taskiq-scheduler`.
- Seed-скрипт `fill_point_db.py` умеет наполнять роли, уровни, компетенции и фейковых пользователей.

## Что важно понимать про текущее состояние

- Проект уже не ограничивается только регистрацией и профилем: в коде есть рабочие сценарии для roles, competencies, broadcasts, notification runtime и health-check.
- В репозитории есть модели задач и решений, но пользовательский Telegram-flow для задач пока не является основным и не описывается как готовая публичная возможность.
- README ниже описывает именно то, что уже есть в кодовой базе сейчас, а не желаемое состояние "на будущее".

## Архитектура

Проект следует `Layered Architecture` с элементами pragmatic DDD.

- `src/pybot/presentation/bot/` - canonical presentation layer for Telegram handlers, dialogs, filters, middlewares, keyboards and runtime wiring.
- `src/pybot/presentation/texts/` - shared user-facing texts and message renderers.
- `src/pybot/services/` - application services и orchestration.
- `src/pybot/infrastructure/` - repositories, adapters, TaskIQ integration, внешние порты.
- `src/pybot/db/` - SQLAlchemy models и database setup.
- `src/pybot/dto/` - DTO и value objects.
- `src/pybot/domain/` - domain exceptions и domain services.
- `src/pybot/di/` - Dishka composition root.
- `src/pybot/presentation/web/` - web presentation API and health server.

Ключевые архитектурные решения зафиксированы в ADR:

- `008` - разделение `find_*` и `get_*` lookup semantics;
- `010` - ports and adapters для внешних интеграций;
- `011` - `TaskIQ + Redis` для фоновых задач и очередей.

## Технологический стек

- `Python 3.12+`
- `aiogram 3.22+`
- `aiogram-dialog 2.4+`
- `Dishka`
- `SQLAlchemy 2` + `aiosqlite`
- `Alembic`
- `Pydantic v2` + `pydantic-settings`
- `Redis`
- `TaskIQ` + `taskiq-redis`
- `FastAPI` + `uvicorn`
- `loguru`
- `uv`
- `ruff`, `ty`, `pytest`, `pytest-aiogram`
- `MkDocs Material`

## Структура репозитория

```text
PyBot_ITAcadem/
├── src/pybot/
│   ├── bot/                  # handlers, dialogs, middlewares, filters, keyboards
│   ├── core/                 # settings, enums, logger
│   ├── db/                   # SQLAlchemy setup и ORM models
│   ├── di/                   # Dishka containers
│   ├── domain/               # domain exceptions и domain services
│   ├── dto/                  # DTO и value objects
│   ├── health/               # FastAPI health app/server
│   ├── infrastructure/       # repositories, adapters, TaskIQ runtime
│   ├── mappers/              # layer mappers
│   ├── services/             # application services
│   └── utils/                # shared utils
├── tests/                    # unit, integration, bot, health, script tests
├── alembic/                  # migrations
├── docs-project/             # MkDocs documentation
├── ansible/                  # deploy/bootstrap playbooks
├── docker-compose.yml
├── docker-compose.prod.yml
├── fill_point_db.py
├── run.py
└── db_reset_start.py
```

## Локальный запуск

### 1. Требования

- `Python 3.12+`
- `uv`
- `just` - желательно, но не обязательно
- `Redis` - нужен только если вы хотите локально использовать `FSM_STORAGE_BACKEND=redis` или поднимать полный Docker runtime

### 2. Установка зависимостей

```bash
git clone https://github.com/NikkiShuRA/PyBot-ITAcadem.git
cd PyBot-ITAcadem
uv sync --all-groups
```

Если нужна только основная среда без dev/doc extras:

```bash
uv sync
```

### 3. Настройте `.env`

Минимальный рабочий пример для локальной разработки:

```env
BOT_TOKEN=your_production_bot_token
BOT_TOKEN_TEST=your_test_bot_token
BOT_MODE=test

DATABASE_URL=sqlite+aiosqlite:///./pybot_itacadem.db

ROLE_REQUEST_ADMIN_TG_ID=123456789
AUTO_ADMIN_TELEGRAM_IDS=

NOTIFICATION_BACKEND=telegram
TELEGRAM_PROXY_URL=
RUNTIME_ALERTS_ENABLED=false
RUNTIME_ALERTS_CHAT_ID=
FSM_STORAGE_BACKEND=memory
REDIS_URL=redis://localhost:6379/0

LOG_LEVEL=INFO
DEBUG=false

HEALTH_API_ENABLED=false
HEALTH_API_HOST=127.0.0.1
HEALTH_API_PORT=8001
```

Что важно:

- сейчас `settings` требуют и `BOT_TOKEN`, и `BOT_TOKEN_TEST`, даже если вы запускаете только один режим;
- `BOT_MODE=test` использует `BOT_TOKEN_TEST`, `BOT_MODE=prod` использует `BOT_TOKEN`;
- `ROLE_REQUEST_ADMIN_TG_ID` обязателен, потому что role request flow уже является частью рабочего сценария;
- `TELEGRAM_PROXY_URL` опционален и нужен только там, где Telegram Bot API доступен через proxy;
- `RUNTIME_ALERTS_ENABLED` и `RUNTIME_ALERTS_CHAT_ID` опциональны и включают runtime alerts только для основного bot-процесса;
- при `FSM_STORAGE_BACKEND=memory` Redis для обычного локального запуска не нужен.

### 4. Примените миграции

```bash
uv run alembic upgrade head
```

Это локальный эквивалент one-shot process type `migrate`. Его запускают явно перед первым стартом или после изменений схемы. В Docker Compose этому соответствует `docker compose --profile migration run --rm migrate`.

### 5. При необходимости заполните БД тестовыми данными

```bash
uv run python fill_point_db.py --help
uv run python fill_point_db.py
```

Это локальный эквивалент one-shot process type `seed`. Он не считается частью обычного runtime-старта и запускается только тогда, когда нужен initial/test seed. В Docker Compose этому соответствует `docker compose --profile seed run --rm seed`.

Скрипт умеет отдельно включать и отключать:

- уровни;
- роли;
- компетенции;
- фейковых пользователей.

### 6. Запустите бота

```bash
uv run run.py
```

или:

```bash
just run
```

`run.py` запускает только bot process type. Health API запускается отдельным process type через Docker Compose (`health` profile).

## Запуск через Docker Compose

Локальный compose поднимает:

- `bot`
- `taskiq-worker`
- `taskiq-scheduler`
- `redis`
- `health` (optional, `health` profile)

Команда:

```bash
docker compose up --build
```

Эта команда поднимает только runtime-сервисы по умолчанию. `migrate` и `seed` в неё не входят и должны запускаться отдельно как one-shot process types.

To run dedicated health process type:

```bash
HEALTH_API_ENABLED=true COMPOSE_PROFILES=health docker compose up --build
```

Тот же запуск без `COMPOSE_PROFILES`:

```bash
HEALTH_API_ENABLED=true docker compose --profile health up --build
```

Явный local flow для admin one-shot процессов:

```bash
docker compose --profile migration run --rm migrate
docker compose --profile seed run --rm seed
```

Особенности локального compose:

- `migrate` запускается отдельным one-shot сервисом и только явно через `docker compose --profile migration run --rm migrate`;
- `seed` запускается отдельным one-shot сервисом и только явно через `docker compose --profile seed run --rm seed`;
- по умолчанию в compose уже прокинуты `DATABASE_URL`, `TELEGRAM_PROXY_URL`, `FSM_STORAGE_BACKEND=redis` и `REDIS_URL`.

## Проверка качества

Основной обязательный локальный gate:

```bash
just quality-gate
```

Также доступны:

```bash
uv run pytest -q
just docs-build
just test-coverage
```

## Документация

Перед значимыми изменениями по проекту сначала читайте:

1. `README.md`
2. `ARCHITECTURE.md`
3. `CONTRIBUTING.md`
4. `DEPLOYMENT.md`
5. `SECURITY.md`
6. релевантные ADR из `src/pybot/docs/adr/`

Локальный запуск MkDocs:

```bash
uv sync --extra docs
just docs-serve
```

## Production и деплой

В репозитории уже есть production deployment skeleton:

- `docker-compose.prod.yml` - image-based runtime;
- `.github/workflows/deploy.yml` - CD flow;
- `ansible/` - bootstrap/deploy playbooks.

Production compose использует отдельные one-shot сервисы:

- `migrate` - для `alembic upgrade head`;
- `seed` - для управляемого initial seed.

Runtime process types в production те же, что и локально: `bot`, `taskiq-worker`, `taskiq-scheduler`, optional `health`, `redis`.

Кто и когда запускает one-shot процессы:

- `migrate` на каждом production deploy запускает Ansible до `docker compose up -d`;
- `seed` в production запускает Ansible только при `RUN_SEED_ON_DEPLOY=true`;
- в local compose те же `migrate` и `seed` явно запускает сам разработчик или оператор.

Подробнее:

- `DEPLOYMENT.md`
- `ansible/playbooks/deploy.yml`
- `docker-compose.prod.yml`

## Полезные команды

```bash
just
just quality-gate
just docs-build
just migrate-apply
just migrate-create "add new field"
uv run pytest -q
uv run python fill_point_db.py --help
```

## Лицензия

Проект распространяется под лицензией `LICENSE` в корне репозитория.
