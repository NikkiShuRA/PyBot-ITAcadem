# План Milestone MVP (MoSCoW)

## Контекст

- Цель текущего цикла: закрыть milestone через Telegram-бота и довести до стабильного деплоя к концу недели.
- Дедлайн: неделя с **26 февраля 2026** по **1 марта 2026**.
- Фокус: `role requests` + рассылки `@all/role/competence` + операционная готовность.

## Зафиксированные решения

- Канал управления рассылкой: команды бота (не админ-панель в этом цикле).
- ACL рассылки: только `Admin`.
- Компетенции в рассылке: селектор по `slug`.
- Рефактор структуры: мягкое введение `presentation/`, без полного big-bang рефактора.

## Public API / интерфейсы

- Новые команды:
  - `/broadcast @all <текст>`
  - `/broadcast role:<role_name> <текст>`
  - `/broadcast competence:<slug> <текст>`
- Новые настройки:
  - `BOOTSTRAP_ADMIN_TG_ID`
  - `BROADCAST_ALLOWED_ROLES` (по умолчанию: `Admin`)
  - `BROADCAST_RATE_LIMIT_PER_SEC`
  - `BROADCAST_MAX_TEXT_LENGTH`

## MoSCoW (этот цикл)

### Must

- [X] Реализовать массовую рассылку:
  - [X] сервис `BroadcastService`
  - [X] таргетинг `@all`, `role:<role>`, `competence:<slug>`
  - [X] dedup получателей + итоговая статистика отправки
- [X] Реализовать bulk-отправку в Telegram адаптере (`NotificationPort` + infrastructure adapter).
- [X] Добавить handler команды `/broadcast` с RBAC и rate-limit.
- [X] Добавить auto-bootstrap admin по `BOOTSTRAP_ADMIN_TG_ID` при регистрации/первом входе.
- [X] Убрать dev-команды выдачи admin-роли из боевой маршрутизации.
- [ ] Ввести мягкий `presentation`-слой:
  - [ ] `src/pybot/presentation/telegram/...`
  - [ ] `src/pybot/presentation/http/...`
- [ ] оставить shim-реэкспорты на старых путях для совместимости
- [X] Добавить `Dockerfile` и `docker-compose` для деплоя бота с health-check.
- [X] Обновить `/help` под новый функционал рассылки.
- [ ] Обеспечить прохождение quality-gate:
  - [ ] `pytest`
  - [ ] `ruff check`
  - [ ] `ty check`

### Should

- [ ] Рефактор `fill_point_db.py` (убрать legacy-дубли и прямые обходы архитектуры).
- [ ] Минимальный audit-log для операций рассылки/массовых операций.
- [ ] Runbook в README: деплой, smoke-check, rollback-шаги.

### Could

- [ ] CD pipeline деплоя после стабилизации ручного деплоя.
- [ ] Расширенный telemetry/метрики по рассылке.

### Won’t (в этом цикле)

- [ ] Полноценная админ-панель на SQLAdmin + JWT/argon2.
- [ ] Масштабный перенос структуры проекта.
- [ ] Полная реализация подсистемы задач из ТЗ.

## План по дням (до конца недели)

- **Чт–Пт (26–27 фев):**
  - [X] Broadcast domain/app/infrastructure + handler + тесты.
  - [X] ACL/rate-limit + обновление `/help`.
- **Сб (28 фев):**
  - [ ] Мягкая миграция в `presentation/*` + shim-совместимость + фиксы импортов.
- **Вс (1 мар):**
  - [x] Dockerfile + compose + health smoke.
  - [ ] Финальный прогон `pytest/ruff/ty`.
  - [ ] Обновление README/runbook.

## Acceptance criteria

- [X] Команда `/broadcast` работает в 3 режимах: `@all`, `role`, `competence`.
- [X] Не-Admin не может запускать рассылку.
- [X] Ошибки частичной отправки не валят весь batch, статистика корректна.
- [X] Auto-bootstrap admin отрабатывает по конфигу.
- [X] Dev-команды роли не доступны в production-роутерах.
- [X] Бот и health-check поднимаются в контейнерах.
- [ ] `pytest`, `ruff`, `ty` проходят без критических ошибок.

## Риски и ограничения

- Компетенции без отдельной колонки slug: использовать нормализацию `name -> slug` в сервисе/запросе.
- Redis в этом milestone опционален и не блокирует релиз.
- Если всплывут критические баги в `presentation`-переносе: откат к shim-пути без блокировки релиза.
