# PyBot ITAcadem

PyBot ITAcadem — асинхронный Telegram-бот для экосистемы ITAcadem StartUP. Проект покрывает регистрацию пользователей, профиль, роли, баллы, уровни и вспомогательную инфраструктуру вокруг бота.

## Что есть в проекте

- регистрация пользователя через Telegram и номер телефона;
- профиль с баллами и уровнями;
- role-based доступ и запросы ролей;
- сервисы рассылок и фоновые задачи через TaskIQ;
- health API, DI на Dishka и SQLite как основная база MVP.

## Быстрый старт для разработки

```bash
git clone https://github.com/NikkiShuRA/PyBot-ITAcadem.git
cd PyBot_ITAcadem
uv sync
just quality-gate
```

## Документация по разделам

- [Руководство пользователя](user-guide/index.md) — как запускать и использовать бота.
- [Руководство разработчика](developer-guide/index.md) — архитектура, разработка, тесты и деплой.
- [Справочник API](api-reference/index.md) — автогенерируемая документация по модулям `src/pybot`.

## Документация как часть кода

Сайт на MkDocs Material собирается из каталога `docs-project/`. Для локальной проверки используйте:

```bash
just docs-install
just docs-build
```
