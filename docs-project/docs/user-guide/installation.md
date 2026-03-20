# Установка

Канонические инструкции по локальному запуску находятся в корневом `README.md`. Ниже краткая версия, синхронизированная с текущим проектом.

## Требования

- Python 3.12+
- `uv`
- доступ к Telegram Bot API

## Шаги

```bash
git clone https://github.com/NikkiShuRA/PyBot-ITAcadem.git
cd PyBot_ITAcadem
uv sync
```

Создайте `.env` на основе `.env.example` и задайте как минимум:

- `BOT_TOKEN`
- `BOT_TOKEN_TEST`
- `ROLE_REQUEST_ADMIN_TG_ID`
- `DATABASE_URL`

После этого можно применить миграции и запустить бота:

```bash
uv run alembic upgrade head
uv run run.py
```

## Для документации

Чтобы локально собирать сайт на MkDocs Material:

```bash
just docs-install
just docs-build
```
