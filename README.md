# 🤖 PyBot_ITAcadem

**PyBot_ITAcadem** — полнофункциональный асинхронный Telegram-бот на Python с поддержкой управления пользователями, проектами, задачами и их комментариями.

Проект использует `aiogram` 3.x для работы с Telegram API, `SQLAlchemy` для ORM, `asyncpg` для асинхронного доступа к PostgreSQL.

## 🚀 Основные возможности

- ✅ **Асинхронная архитектура** — использует `asyncio`, `aiogram`, `asyncpg`
- 👥 **Управление пользователями** — роли (администратор, академическая роль), компетенции, достижения
- 📁 **Управление проектами** — создание, редактирование, статусы, участники, роли в проектах
- ✍️ **Управление задачами** — задачи, решения, комментарии, вложения
- 💬 **Система комментариев** — комментарии на задачи, решения и вложения
- 📎 **Вложения** — поддержка различных типов вложений для задач и комментариев
- 🔐 **Аутентификация** — обработчики авторизации в `handlers/auth.py`
- 🗄️ **ORM с SQLAlchemy** — типизированные модели данных по модулям

## 📋 Требования

- Python 3.10+
- PostgreSQL 12+
- aiogram 3.x
- SQLAlchemy 2.x
- asyncpg
- python-dotenv

## 🔧 Установка и настройка

### 1. Клонирование репозитория

```powershell
git clone https://github.com/NikkiShuRA/PyBot.git
cd PyBot
```

### 2. Создание виртуального окружения

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

### 3. Установка зависимостей

```powershell
pip install aiogram sqlalchemy[asyncio] asyncpg python-dotenv
```

### 4. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Telegram Bot Token (используется BOT_TOKEN_TEST для тестирования)
BOT_TOKEN=YOUR_PROD_BOT_TOKEN_HERE
BOT_TOKEN_TEST=YOUR_TEST_BOT_TOKEN_HERE

# PostgreSQL Connection
DB_USER=postgres
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pybot_db
```

### 5. Запуск бота

```powershell
python run.py
```

## 📁 Структура проекта

```
PyBot/
├── run.py                          # Точка входа
├── config.py                       # Конфигурация (переменные окружения)
├── LICENSE                         # MIT License
├── README.md                       # Этот файл
│
├── db_class/                       # Слой работы с БД
│   ├── base_class.py              # Базовая конфигурация ORM
│   ├── database.py                # SessionLocal, init_db()
│   └── models/                    # SQLAlchemy модели
│       ├── achievement.py
│       ├── attachments.py
│       ├── comment_answers.py
│       ├── comment_attachments.py
│       ├── comments.py
│       ├── attachments_types.py
│       ├── user_module/           # Пользователи и их роли
│       │   ├── user.py
│       │   ├── academic_role.py
│       │   ├── admin_role.py
│       │   ├── competence.py
│       │   ├── level.py
│       │   ├── user_achievement.py
│       │   ├── user_activityStatus.py
│       │   ├── user_competence.py
│       │   ├── user_tasks.py
│       │   └── valuation.py
│       ├── project_module/        # Проекты
│       │   ├── projects.py
│       │   ├── project_members.py
│       │   ├── project_member_roles.py
│       │   ├── project_achievements.py
│       │   ├── project_attachments.py
│       │   ├── project_comments.py
│       │   └── projects_statuses.py
│       └── task_module/           # Задачи
│           ├── tasks.py
│           ├── task_solutions.py
│           ├── task_solution_statuses.py
│           ├── task_attachments.py
│           ├── task_comments.py
│           └── task_solution_comments.py
│
├── services/                       # Бизнес-логика
│   ├── users.py                   # Сервисы для работы с пользователями
│   └── attachment.py              # Сервисы для работы с вложениями
│
├── tg_bot/                         # Основной пакет бота
│   ├── tg_bot_run.py              # Запуск бота (tg_bot_main)
│   ├── filters/                   # Пользовательские фильтры aiogram
│   ├── keyboards/                 # Клавиатуры и callback-кнопки
│   └── handlers/                  # Обработчики сообщений
│       ├── auth.py                # Аутентификация
│       ├── test.py
│       ├── admin/                 # Админ-команды
│       ├── common/                # Общие команды
│       │   ├── start.py          # /start
│       │   └── misc.py
│       ├── projects/              # Работа с проектами
│       ├── tasks/                 # Работа с задачами
│       └── user/                  # Профиль и данные пользователя
```

## 🔑 Переменные окружения

| Переменная | Описание | Пример |
|-----------|---------|--------|
| `BOT_TOKEN` | Токен бота для production | `123456:ABC-DEF1234567` |
| `BOT_TOKEN_TEST` | Токен бота для тестирования | `987654:XYZ-ABC9876543` |
| `DB_USER` | Пользователь PostgreSQL | `postgres` |
| `DB_PASS` | Пароль PostgreSQL | `secret_password` |
| `DB_HOST` | Хост БД | `localhost` |
| `DB_PORT` | Порт PostgreSQL | `5432` |
| `DB_NAME` | Название БД | `pybot_db` |

## 🏗️ Архитектура

### Middleware
- **DbSessionMiddleware** — автоматически подключает сессию БД ко всем обработчикам сообщений

### Обработчики (Handlers)
Используют `aiogram` Router для маршрутизации команд и сообщений. Организованы по модулям:
- `auth` — логика входа/регистрации
- `common` — общие команды (`/start`)
- `admin` — администраторские функции
- `projects` — работа с проектами
- `tasks` — работа с задачами
- `user` — работа с пользователем

### Сервисы (Services)
Содержат бизнес-логику, отделённую от обработчиков:
- `users.py` — работа с пользователями и их данными
- `attachment.py` — управление вложениями

### Модели (Models)
Используют SQLAlchemy для описания таблиц. Разделены по функциональным модулям:
- **user_module** — пользователи, роли, компетенции, достижения
- **project_module** — проекты, члены, роли, комментарии
- **task_module** — задачи, решения, комментарии, статусы

## 🚀 Запуск локально

### С локальным PostgreSQL

Убедитесь, что PostgreSQL запущена и доступна по адресу из `.env`, затем:

```powershell
python run.py
```

## 📝 Примеры использования

После успешного запуска бот будет ожидать команд от пользователей через Telegram:

```
/start          - Начать общение с ботом
/help           - Справка по командам
/profile        - Мой профиль
/projects       - Мои проекты
/tasks          - Мои задачи
```

## 📄 Лицензия

MIT License — см. файл [LICENSE](LICENSE)

Copyright (c) 2025 [NikkiShuRA](https://github.com/NikkiShuRA)

---

**Создано**: 2025 | **Автор**: NikkiShuRA | **Лицензия**: MIT

