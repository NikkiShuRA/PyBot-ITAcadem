# ADR 0010: Введение портов и адаптеров для внешних интеграций

## Дата: 19-03-2026

## Статус: Accepted

## Контекст

Проекту понадобилось сохранить application layer независимым от конкретных внешних интеграций, прежде всего от Telegram Bot API, логового режима уведомлений и будущих вариантов transport/runtime delivery.

Если application services начинают напрямую зависеть от инфраструктурных клиентов и transport-specific API, то:

- use-case логика становится связанной с конкретной реализацией;
- тестирование усложняется, потому что приходится поднимать или глубоко мокать внешний транспорт;
- замена или добавление новой интеграции начинает тянуть изменения по всей application layer;
- границы между business orchestration и infrastructure размываются.

Проект уже использует Dishka и layered architecture, поэтому внешние взаимодействия должны встраиваться в неё через явные контракты.

## Решение

Принято решение использовать порты на стороне application layer и адаптеры на стороне infrastructure layer для всех внешних интеграций, которые нужны сервисам, но не должны диктовать им свою реализацию.

### Детали реализации

1. На стороне application layer вводятся контракты-порты:

   - `NotificationPort` для синхронной отправки уведомлений во внешний транспорт;
   - `NotificationDispatchPort` для диспетчеризации уведомлений в background/schedule runtime.

2. На стороне infrastructure layer вводятся адаптеры:

   - `TelegramNotificationService` как transport adapter для Telegram;
   - `LoggingNotificationService` как безопасный логовый adapter для локального и fallback-сценария;
   - `TaskIQNotificationDispatcher` как adapter для background dispatch через очередь задач.

3. Application services и фасады зависят от портов, а не от concrete implementation:

   - `RoleRequestService` и `BroadcastService` работают через `NotificationPort`;
   - `NotificationFacade` работает через `NotificationDispatchPort`.

4. Конкретные реализации выбираются в composition root через Dishka providers.

### Архитектура

```text
Application service / facade
    |
    v
Port (contract)
    |
    +--> Telegram adapter
    +--> Logging adapter
    +--> Background dispatch adapter
```

Таким образом, application layer знает только семантику операции, но не знает конкретный transport/runtime implementation.

## Альтернативы

* **Вызывать внешние клиенты напрямую из services:**
  * *Плюсы:* Меньше абстракций и меньше файлов.
  * *Минусы:* Сильная связность application layer с инфраструктурой, сложнее тестировать и сложнее заменять transport implementation.

* **Использовать один общий adapter без разделения на порты:**
  * *Плюсы:* Быстрее стартовая реализация.
  * *Минусы:* Смешиваются разные семантики: синхронная отправка, dispatch в очередь, fallback-режимы и transport details.

## Последствия

### Положительные

* [+] Application services остаются изолированными от transport-specific API.
* [+] Тестирование становится проще за счёт подмены портов stub/mock реализациями.
* [+] Новые внешние интеграции добавляются через adapters без переписывания use-case логики.
* [+] Решение хорошо сочетается с текущим DI и layering проекта.

### Отрицательные

* [-] Появляется дополнительный слой абстракции, который нужно поддерживать в актуальном состоянии.
* [-] Для новых участников проекта порты/адаптеры требуют краткого архитектурного онбординга.

## Ссылки

* [ADR 0009: Минимальный контракт событийного логирования](009-minimal-logging-event-contract.md)
* [ADR 0011: Использование TaskIQ и Redis для фоновых задач и очереди сообщений](011-taskiq-background-runtime-and-message-queue.md)
* [src/pybot/services/ports/notification_port.py](../../services/ports/notification_port.py)
* [src/pybot/services/ports/notification_dispatch_port.py](../../services/ports/notification_dispatch_port.py)
* [src/pybot/services/notification_facade.py](../../services/notification_facade.py)
* [src/pybot/infrastructure/ports/telegram_notification_service.py](../../infrastructure/ports/telegram_notification_service.py)
* [src/pybot/infrastructure/ports/logging_notification_service.py](../../infrastructure/ports/logging_notification_service.py)
* [src/pybot/di/containers.py](../../di/containers.py)
