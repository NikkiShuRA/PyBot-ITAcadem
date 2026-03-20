# ADR 0011: Использование TaskIQ и Redis для фоновых задач и очереди сообщений

## Дата: 19-03-2026

## Статус: Accepted

## Контекст

После введения портов и адаптеров проекту понадобился отдельный механизм для фонового выполнения задач, отложенных уведомлений и scheduler-based dispatch.

Если выполнять такие операции только синхронно в рамках Telegram update handler, то:

- долгие операции начинают ухудшать UX и задерживать ответы бота;
- невозможно нормально поддерживать delayed и periodic execution;
- dispatch и execution оказываются слишком жёстко привязаны к основному bot runtime;
- эксплуатация background-подсистемы становится непрозрачной.

Проект уже использует Redis и Dishka, поэтому нужен был относительно лёгкий background stack, который:

- поддерживает очереди и scheduling;
- не требует избыточного operational overhead;
- хорошо встраивается в текущий async runtime и DI-подход.

## Решение

Принято решение использовать `TaskIQ + Redis` как механизм background execution, очереди сообщений и scheduler runtime.

### Детали реализации

1. `RedisStreamBroker` используется как broker для worker runtime.
2. `ListRedisScheduleSource` используется как источник отложенных, interval и cron-задач.
3. `TaskiqScheduler` собирается как отдельный scheduler runtime.
4. `TaskIQNotificationDispatcher` ставит сообщения в очередь или schedule source через producer-side API.
5. Реальное выполнение происходит в отдельных процессах:

   - `bot` отвечает за пользовательский runtime;
   - `taskiq-worker` исполняет фоновые задачи;
   - `taskiq-scheduler` управляет отложенными и cron-задачами.

6. Dishka интегрируется с TaskIQ через lifecycle hooks worker runtime, чтобы фоновые задачи получали зависимости из согласованного DI-контейнера.

### Архитектура

```text
Producer side
NotificationFacade / TaskIQNotificationDispatcher
    |
    v
TaskIQ broker / schedule source
    |
    +--> worker runtime -> task execution
    |
    +--> scheduler runtime -> delayed / interval / cron dispatch
```

Это разделяет постановку задачи в очередь и её фактическое исполнение.

## Альтернативы

* **Оставить только синхронное выполнение без очереди:**
  * *Плюсы:* Самая простая схема.
  * *Минусы:* Нет delayed/cron задач, долгие операции начинают мешать обработке update, хуже масштабируется operationally.

* **Выбрать более тяжёлый background stack, например Celery:**
  * *Плюсы:* Более известный и мощный ecosystem.
  * *Минусы:* Лишний overhead для текущего размера проекта и более тяжёлое сопровождение перед короткими дедлайнами.

* **Запускать периодические и фоновые действия внутри основного bot process:**
  * *Плюсы:* Меньше runtime-компонентов.
  * *Минусы:* Хуже изоляция, выше риск влиять на responsiveness бота, слабее эксплуатационная предсказуемость.

## Последствия

### Положительные

* [+] Фоновые задачи и scheduling отделены от основного bot loop.
* [+] Появляется нормальный механизм delayed/interval/cron dispatch.
* [+] Runtime становится ближе к production-ready схеме с выделенными worker/scheduler процессами.
* [+] Решение остаётся относительно лёгким по сравнению с более тяжёлыми queue stacks.

### Отрицательные

* [-] Появляется дополнительный operational контур: worker и scheduler надо деплоить и проверять отдельно.
* [-] Ошибки background execution могут быть менее очевидны без хороших логов и runbook.
* [-] Очередь и scheduler зависят от корректной работы Redis runtime.

## Ссылки

* [ADR 0009: Минимальный контракт событийного логирования](009-minimal-logging-event-contract.md)
* [ADR 0010: Введение портов и адаптеров для внешних интеграций](010-ports-and-adapters-for-external-integrations.md)
* [src/pybot/infrastructure/taskiq/taskiq_app.py](../../infrastructure/taskiq/taskiq_app.py)
* [src/pybot/infrastructure/taskiq/taskiq_notification_dispatcher.py](../../infrastructure/taskiq/taskiq_notification_dispatcher.py)
* [src/pybot/infrastructure/taskiq/tasks/notification.py](../../infrastructure/taskiq/tasks/notification.py)
* [src/pybot/services/notification_facade.py](../../services/notification_facade.py)
* [src/pybot/di/containers.py](../../di/containers.py)
* [docker-compose.prod.yml](../../../../docker-compose.prod.yml)
