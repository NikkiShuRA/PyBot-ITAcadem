# Деплой

Полное описание деплоя находится в корневом `DEPLOYMENT.md`. Эта страница дает быстрый обзор для навигации в сайте документации.

## Базовый контур

1. CI на `main` должен пройти успешно.
2. Workflow `CD - Build and Deploy` собирает Docker image и публикует его в GHCR.
3. Ansible разворачивает `docker-compose.prod.yml` на сервере.
4. Отдельный migration-контейнер применяет миграции.
5. Выполняется post-deploy smoke-check.

## Ключевые файлы

- `docker-compose.prod.yml`
- `.github/workflows/deploy.yml`
- `ansible/playbooks/bootstrap.yml`
- `ansible/playbooks/deploy.yml`

## Что не забывать

- синхронизировать `.env.example` и runtime config;
- учитывать SQLite-ограничения в миграциях;
- документировать rollback и operator steps, если изменение не backward-compatible.
