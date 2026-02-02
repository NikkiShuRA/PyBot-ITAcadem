# PyBot ITAcadem 🚀

Привет! Мы разрабатываем этот Telegram‑бот для ITAcadem StartUP.
Цель проекта — дать участникам простой вход в экосистему академии: авторизация по номеру телефона, создание профиля и в дальнейшем работа с задачами, проектами и достижениями.

---

## О чём этот бот 🤖

Сейчас бот решает базовую, но важную задачу — идентификация и онбординг участника:

- Авторизация через Telegram и номер телефона.
- Привязка Telegram‑аккаунта к уже существующему пользователю по телефону.
- Создание нового профиля через удобный диалог.
- Несколько базовых команд для навигации и проверки, что бот жив.

При этом под капотом уже лежит полноценная модель данных для пользователей, проектов, задач, комментариев и достижений — фундамент, на котором дальше можно строить геймификацию и управление учёбой через Telegram.

---

## Что умеет бот сейчас ✅

- `/start` в личке:
  - если пользователь уже известен по Telegram ID — показывает подсказку и готов к работе;
  - если нет — просит отправить контакт, проверяет, что это его номер, и:
    - либо привязывет к существующему пользователю по телефону;
    - либо запускает диалог создания профиля (имя → фамилия → отчество) и сохранет в БД.
- `/start` в группе — просто приветствие без авторизации.
- `/help` — краткая справка по основным командам.
- `/info` — информация об ITAcadem StartUP и ссылке на репозиторий.
- `/ping` — health‑check (отвечает `pong`).

---

## Стек технологий 🛠

- Python 3.11+
- aiogram — работа с Telegram Bot API
- aiogram_dialog — диалоговые сценарии
- SQLAlchemy (async) — ORM и работа с БД в асинхронном режиме
- Alembic — миграции схемы БД
- SQLite / PostgreSQL — поддерживаемые СУБД (в зависимости от строки подключения)
- asyncpg — драйвер для PostgreSQL
- aiosqlite — драйвер для SQLite
- Pydantic + pydantic-settings — модели данных и конфигурация через .env
- loguru — логирование
- Faker — генерация тестовых данных (наполнение БД)
- phonenumbers — нормализация и валидация телефонных номеров

---

## Структура проекта 🌳

Ниже упрощённое дерево, чтобы было понятно, где что лежит:

```plain text
PyBot-ITAcadem/
├── alembic/
│   ├── env.py
│   └── versions/
│       └── ...
├── src/
│   ├── __init__.py
│   └── pybot/
│       ├── __init__.py
│       ├── bot/
│       │   ├── tg_bot_run.py
│       │   ├── dialogs/
│       │   │   ├── __init__.py
│       │   │   └── user/
│       │   │       ├── __init__.py
│       │   │       ├── getters.py
│       │   │       ├── handlers.py
│       │   │       ├── states.py
│       │   │       └── windows.py
│       │   ├── filters/
│       │   │   ├── __init__.py
│       │   │   ├── chat_filters.py
│       │   │   ├── message_value_filters.py
│       │   │   └── router_factories.py
│       │   ├── handlers/
│       │   │   ├── __init__.py
│       │   │   ├── common/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── misc.py
│       │   │   │   └── start.py
│       │   │   └── points/
│       │   │       ├── __init__.py
│       │   │       └── grand_points.py
│       │   ├── keyboards/
│       │   │   ├── __init__.py
│       │   │   └── auth.py
│       │   └── utils/
│       │       ├── __init__.py
│       │       └── text_id_searches.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── constants.py
│       │   └── logger.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── base_class.py
│       │   ├── database.py
│       │   └── models/
│       │       ├── __init__.py
│       │       ├── achievement.py
│       │       ├── level_module/
│       │       │   └── __init__.py
│       │       ├── task_module/
│       │       │   ├── __init__.py
│       │       │   ├── task_solution_statuses.py
│       │       │   ├── task_solutions.py
│       │       │   └── tasks.py
│       │       └── user_module/
│       │           ├── __init__.py
│       │           ├── academic_role.py
│       │           ├── admin_role.py
│       │           ├── competence.py
│       │           ├── level.py
│       │           ├── user.py
│       │           ├── user_achievement.py
│       │           ├── user_activity_status.py
│       │           ├── user_competence.py
│       │           ├── user_level.py
│       │           └── valuation.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── achievement.py
│       │   ├── base.py
│       │   ├── competence.py
│       │   ├── factories.py
│       │   ├── level.py
│       │   ├── role.py
│       │   ├── task.py
│       │   ├── user.py
│       │   ├── valuation.py
│       │   └── value_objects.py
│       ├── dto/
│       │   ├── __init__.py
│       │   ├── base_dto.py
│       │   └── user_dto.py
│       ├── mappers/
│       │   ├── __init__.py
│       │   ├── level_mappers.py
│       │   ├── points_mappers.py
│       │   └── user_mappers.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── levels.py
│       │   ├── points.py
│       │   └── users.py
│       └── utils/
│           ├── __init__.py
│           └── phonenumber_normalization.py
├── __init__.py
├── fill_point_db.py
└── run.py

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
   ```

6. Запустить бота:

   ```bash
   python run.py
   ```

---

## Куда всё движется дальше 📈

То, что сейчас есть — это онбординг и фундамент.
Дальше планируем:

- завязать на бота задачи (выдача, решения, статусы);
- добавить геймификацию: уровни, компетенции, достижения, баллы;
- расширить роли (студент, ментор, админ) и дать им разные возможности прямо в Telegram.

Если хочешь что‑то предложить или помочь с разработкой — форкай, открывай PR или заводи issue 🙂
