# CHANGELOG

<!-- version list -->

## v0.15.0 (2026-02-28)

### Chores

- **dependencies**: Обновление зависимостей в проекте
  ([`1f85d49`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1f85d49f4ac87de0d6710e0b606511da34c765a5))

### Features

- Добавил цветные кнопки и пофиксил блокер конфигурации
  ([#73](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/73),
  [`229b523`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/229b5238bbd2d64fcbf7dc3ce290c6c3d218cd09))

- **bot**: Добавил цветные кнопки для логики запроса роли и улучшил типизацию в тестах
  ([#73](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/73),
  [`229b523`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/229b5238bbd2d64fcbf7dc3ce290c6c3d218cd09))

- **UX**: Добавил цветовое кодирование для кнопок
  ([#73](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/73),
  [`229b523`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/229b5238bbd2d64fcbf7dc3ce290c6c3d218cd09))


## v0.14.1 (2026-02-28)


## v0.14.0 (2026-02-28)

### Bug Fixes

- Вернул delete_webhook для бота
  ([`984b2eb`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/984b2ebed3aa185ef6cb2963091c8c5d655f39ce))

- Добавил отвязку клавиатуры при вводе контакта при регистрации
  ([`84eb792`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/84eb7927db915df62958b869bd5c111d486cfc85))

- Изменил логику валидации, приведя её в вид более соотвествующий поставленным бизнесс требованиям
  ([`adafbe9`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/adafbe936bd8e9ed42a541547d15be0494c15f82))

- Исправил Mojibake в сообщениях запроса роли
  ([`5fcd5cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/5fcd5cc94afc8f94e6d0ac38820c997c58aa78ee))

- Исправил логику проверки ролей, добавив возможность эффективного обрабатывать множество ролей на
  одном хэндлере, диалоге
  ([`a549d11`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a549d11e2ed71555d24b9cf564d57fc39046e2c3))

- Исправил ошибку с незавершением диалога регистрации
  ([`ff9e69f`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/ff9e69fcef8e449d84f6076d0e4f103dc80f2092))

- Перешёл на более стабильную версию функционала ruff из-за ошибки парсинга run.py при запуске
  линтера
  ([`cca3514`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/cca3514e5dda5028fd9514a3fe1a1c866bbf34b4))

- Убрал enqueue=True из логгера для исправления блокировки программы при её завершении
  ([`0015d83`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/0015d831983c2d296d445c36185788d4cdb98926))

- Убрал не используемую заглушку ошибки в скрипте
  ([`5bc0595`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/5bc0595ca75badc8002abafd2f255eda93864dbb))

- **deployment**: Исправление ошибки сохранения FSM в Redis в aiogrma-dialog
  ([`6b31ef4`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/6b31ef4b7020d990d59c39a3ca94df0f78a04ac6))

### Chores

- **dependencies**: Изменил uv.lock
  ([`c3bd870`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/c3bd8707982378cbdca68f28f8b566ee2bc2fe41))

- **deploy**: Добавил базовые dockerfile и docker-compose.yaml
  ([`5a7ecdf`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/5a7ecdf565d2b2e884114ebc317d2981e050a971))

- **deploy**: Добавил использование миграций базы данных, также скрипта её заполнения при деплое, а
  также использование .env для получения данных
  ([`b232f13`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b232f13899b6eea6137907b8bf1faafc3c34604a))

- **deploy**: Пофиксил ошибку с байтами с BOM-рисками
  ([`8156f47`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8156f47f9b61861ec419f579f0f727c13b8b8744))

- **docs**: Обновил /help для большего отражения текущего состояния проекта
  ([`96f598c`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/96f598cd73c4ecc5858ffb800e35afd403e21af0))

- **format**: Применил markdownlint для исправления ошибок форматирования в плане развития проекта
  ([`8092805`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8092805017b10f1ecbf29a5153248f2188080920))

- **test**: Добавление тестов в CI-pipeline, создание инфраструктуры для тестов, создание первой
  волны интеграционных тестов
  ([`e39da4c`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e39da4c4ebb53d206e7d576cf8d6314be8db7aa8))

### Documentation

- **README**: Добавил раздел Runbook для запуска бота и внесения в него изменений
  ([`7e19e2b`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7e19e2b16c400c5783cf809e8b0974d7f46daec2))

### Features

- Добавил rate-limiting для команды рассылки
  ([`9baedb1`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/9baedb176a0d16a94b144180a6f8ce37279ca848))

- Добавил ratelimting и role limiting для текущих handler-ов, где это необходимо
  ([`8eadc18`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8eadc18f4ab7c7551084596330fa5bd691b56c3a))

- Добавил автодобавление роли админа при регистрации, по telegram id в конфигурации и удалил
  dev-команду /admin
  ([`b0e54be`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b0e54bee2228ed297ec0768ae0b5d546f806489e))

- Добавил поддержку Redis для хранения FSM
  ([`7248e39`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7248e39d638ec53d2e18e7743ce6b70a5dcee4fe))

- Добавил реализацию NotificationPort, которая отправляет сообщения в логгер
  ([`30dae28`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/30dae287c7603b9ca066cfa98d65867a0c6f413d))

- Добавил фильтер для conditional UI в aiogram-dialog, с добавлением списка ролей пользователя в
  данные из middleware
  ([`6e00087`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/6e000872aeacffde67057e5e5db0df2b9d350fbe))

- Добавил хэндлеры для запроса роли у администратора
  ([`cea37db`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/cea37db70db0449615f134b6b96d131ab4f823de))

- Завершение функциональности рассылки в боте
  ([`e49ef04`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e49ef0422581e299c63f1425ef347dfd659beafc))

- Завершил бизнес-логику запроса роли у администратора
  ([`bf01dd2`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/bf01dd29511a8207f48be5bcac2a66f60590530a))

- Реализовал сервис для отправки сообщений в телеграмм
  ([`2aa1f8d`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/2aa1f8d062f1c84cd4cc1cf4cbea35a6acb0e6be))

- Реализовал ядро бизнес-логики для работы с компетенциями
  ([`2d54c71`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/2d54c7123ddf0168cdc6f7fd7056f5b00fe84783))

- Сделал первый полный flow системы рассылок, по ролям и по @all
  ([`f0f29b9`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/f0f29b909845bcebcfa9f73d24a0c6cb5e19aad3))

### Refactoring

- Добавил VO в объекты кода, и инструменты в CI-pipeline
  ([`5436feb`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/5436feb66e7d773568b6aed86fa743267a4d2823))


## v0.13.0 (2026-02-25)

### Bug Fixes

- Вернул delete_webhook для бота ([#71](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/71),
  [`aabe7ea`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/aabe7ea3e26da5420a06337d04e52b9a9729b612))

- Исправил логику проверки ролей, добавив возможность эффективного обрабатывать множество ролей на
  одном хэндлере, диалоге ([#71](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/71),
  [`aabe7ea`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/aabe7ea3e26da5420a06337d04e52b9a9729b612))

- Убрал enqueue=True из логгера для исправления блокировки программы при её завершении
  ([#71](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/71),
  [`aabe7ea`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/aabe7ea3e26da5420a06337d04e52b9a9729b612))

### Chores

- **test**: Добавление тестов в CI-pipeline, создание инфраструктуры для тестов, создание первой
  волны интеграционных тестов ([#71](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/71),
  [`aabe7ea`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/aabe7ea3e26da5420a06337d04e52b9a9729b612))

### Features

- Добавил фильтер для conditional UI в aiogram-dialog, с добавлением списка ролей пользователя в
  данные из middleware ([#71](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/71),
  [`aabe7ea`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/aabe7ea3e26da5420a06337d04e52b9a9729b612))

- Добавил хэндлеры для запроса роли у администратора
  ([#71](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/71),
  [`aabe7ea`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/aabe7ea3e26da5420a06337d04e52b9a9729b612))

- Завершил бизнес-логику запроса роли у администратора
  ([#71](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/71),
  [`aabe7ea`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/aabe7ea3e26da5420a06337d04e52b9a9729b612))

- Реализовал сервис для отправки сообщений в телеграмм
  ([#71](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/71),
  [`aabe7ea`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/aabe7ea3e26da5420a06337d04e52b9a9729b612))

- **role-request**: Завершил flow запроса роли у админа и стабилизировал callback/coverage тесты
  ([#71](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/71),
  [`aabe7ea`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/aabe7ea3e26da5420a06337d04e52b9a9729b612))

### Refactoring

- Добавил VO в объекты кода, и инструменты в CI-pipeline
  ([#71](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/71),
  [`aabe7ea`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/aabe7ea3e26da5420a06337d04e52b9a9729b612))


## v0.12.0 (2026-02-23)

### Bug Fixes

- Исправил логику проверки ролей, добавив возможность эффективного обрабатывать множество ролей на
  одном хэндлере, диалоге
  ([`fd55f11`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/fd55f11fc355cf6926f3b5b58b6a437e88c7f993))

- Убрал enqueue=True из логгера для исправления блокировки программы при её завершении
  ([`fd55f11`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/fd55f11fc355cf6926f3b5b58b6a437e88c7f993))

### Chores

- **docs**: Подправил форматированиеи в JUSTFILE
  ([`d5468ed`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/d5468edce5faa5eb9bf913be86fa362190eb5d21))

- **docs**: Улучшил документацию за счёт добавления docstrings, атрибутов декораторов,
  Query-параметров, примеров данных, добавления подробных Fields в DTO
  ([`fd55f11`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/fd55f11fc355cf6926f3b5b58b6a437e88c7f993))

### Features

- Добавил фильтер для conditional UI в aiogram-dialog, с добавлением списка ролей пользователя в
  данные из middleware
  ([`fd55f11`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/fd55f11fc355cf6926f3b5b58b6a437e88c7f993))

- **healthcheck**: Добавил FastAPI эндпоинты для проверки жизнеспособности системы и её готовности
  ([`fd55f11`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/fd55f11fc355cf6926f3b5b58b6a437e88c7f993))

### Refactoring

- Добавил VO в объекты кода, и инструменты в CI-pipeline
  ([`fd55f11`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/fd55f11fc355cf6926f3b5b58b6a437e88c7f993))


## v0.11.0 (2026-02-21)

### Bug Fixes

- Исправил импорт в сервисе запроса ролей
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Исправил логику проверки ролей, добавив возможность эффективного обрабатывать множество ролей на
  одном хэндлере, диалоге ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Исправил ошибку с Missing greenlet при обновлении данных
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Убрал enqueue=True из логгера для исправления блокировки программы при её завершении
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

### Chores

- **dependency**: Перенёс зависимость pytest-coverage в dev
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- **dependency**: Убрал неиспользуемую зависимость uvicorn
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- **dx**: Добавить justfile для кроссплатформенного task runner-а для аналога make
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- **test**: Добавление тестов на сборку бота, а также на корректность работы DI-контейнера
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

### Features

- Добавил justfile для дальнейшей замены makefile-а
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Добавил метод для Rich ORM Model RoleRequest
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Добавил модель для запросов ролей и Enums для статуса запроса
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Добавил фильтер для conditional UI в aiogram-dialog, с добавлением списка ролей пользователя в
  данные из middleware ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Создал полноценный репозиторий для RoleRequest для создания flow отправки запроса роли
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Создал фабрику для создания клавиатуры и функцию для её использования, добавил заготовку для
  сервиса запросов ролей ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Создание dto, и репозитория запросов ролей для функциональности
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

### Refactoring

- Добавил VO в объекты кода, и инструменты в CI-pipeline
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Добавил поддержку изменения bot token-а через .env для повышения универсальности кода, без
  вмешательство в него, для будущей интеграции Docker-а
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Изменения оповещений на английские, удаление лишних комментариев, замена создания instance-а bot-а
  на использование DI-контейнера ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Исправил обработку ошибок в tg_bot_main за счёт того, улучшив gracefull shutdown
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))

- Перенос создания instances bot-а из aiogram в DI-контейнер
  ([#69](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/69),
  [`b4d95cc`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b4d95cc9a69fe282956d9bb02c23eb8200408a75))


## v0.10.0 (2026-02-21)

### Bug Fixes

- Исправил импорт в сервисе запроса ролей
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- Исправил логику проверки ролей, добавив возможность эффективного обрабатывать множество ролей на
  одном хэндлере, диалоге ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- Исправил ошибку с Missing greenlet при обновлении данных
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- Убрал enqueue=True из логгера для исправления блокировки программы при её завершении
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

### Chores

- **dependency**: Перенёс зависимость pytest-coverage в dev
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- **dependency**: Убрал неиспользуемую зависимость uvicorn
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- **test**: Добавление тестов на сборку бота, а также на корректность работы DI-контейнера
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

### Features

- Добавил метод для Rich ORM Model RoleRequest
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- Добавил модель для запросов ролей и Enums для статуса запроса
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- Добавил фильтер для conditional UI в aiogram-dialog, с добавлением списка ролей пользователя в
  данные из middleware ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- Создал полноценный репозиторий для RoleRequest для создания flow отправки запроса роли
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- Создал фабрику для создания клавиатуры и функцию для её использования, добавил заготовку для
  сервиса запросов ролей ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- Создание dto, и репозитория запросов ролей для функциональности
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

### Refactoring

- Добавил VO в объекты кода, и инструменты в CI-pipeline
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- Изменения оповещений на английские, удаление лишних комментариев, замена создания instance-а bot-а
  на использование DI-контейнера ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))

- Перенос создания instances bot-а из aiogram в DI-контейнер
  ([#68](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/68),
  [`1a2f456`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1a2f4567866e69abcbcd2edaada3bd6fd8c6b192))


## v0.9.0 (2026-02-13)

### Bug Fixes

- Исправил импорт в сервисе запроса ролей
  ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

- Исправил логику проверки ролей, добавив возможность эффективного обрабатывать множество ролей на
  одном хэндлере, диалоге ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

- Исправил ошибку Missing greenlet при обновлении баллов с изменением уровня
  ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

- Исправил ошибку с Missing greenlet при обновлении данных
  ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

- Убрал enqueue=True из логгера для исправления блокировки программы при её завершении
  ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

### Features

- Добавил метод для Rich ORM Model RoleRequest
  ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

- Добавил модель для запросов ролей и Enums для статуса запроса
  ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

- Добавил фильтер для conditional UI в aiogram-dialog, с добавлением списка ролей пользователя в
  данные из middleware ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

- Создал полноценный репозиторий для RoleRequest для создания flow отправки запроса роли
  ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

- Создал фабрику для создания клавиатуры и функцию для её использования, добавил заготовку для
  сервиса запросов ролей ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

- Создание dto, и репозитория запросов ролей для функциональности
  ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))

### Refactoring

- Добавил VO в объекты кода, и инструменты в CI-pipeline
  ([#62](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/62),
  [`a7af223`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a7af223347fbc0a3aa990e1bf264bdaa519e9664))


## v0.8.0 (2026-02-05)

### Features

- Добавил функции для ручного изменения ролей
  ([#61](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/61),
  [`7c78738`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7c7873847e9b45b389ea76fbc51ac03b876090d2))

### Refactoring

- Добавил пользовательские ошибки для доменной логики, бизнес-логики и Репозиториев для повышения
  качетсва обработки ошибок ([#61](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/61),
  [`7c78738`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7c7873847e9b45b389ea76fbc51ac03b876090d2))

- Организация импортов ([#61](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/61),
  [`7c78738`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7c7873847e9b45b389ea76fbc51ac03b876090d2))

### Testing

- Добавил базовые unit-тесты для кода ([#61](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/61),
  [`7c78738`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7c7873847e9b45b389ea76fbc51ac03b876090d2))

- Добавил базовые unit-тесты для проекта
  ([#61](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/61),
  [`7c78738`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7c7873847e9b45b389ea76fbc51ac03b876090d2))


## v0.7.0 (2026-02-05)

### Bug Fixes

- Full gracefull shutdown ([#60](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/60),
  [`7e3a138`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7e3a138db9e6dd5e0a9bab46a1dc663ef7d25943))

### Features

- Добавил функции для ручного изменения ролей
  ([#60](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/60),
  [`7e3a138`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7e3a138db9e6dd5e0a9bab46a1dc663ef7d25943))

### Refactoring

- Добавил пользовательские ошибки для доменной логики, бизнес-логики и Репозиториев для повышения
  качетсва обработки ошибок ([#60](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/60),
  [`7e3a138`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7e3a138db9e6dd5e0a9bab46a1dc663ef7d25943))

- Организация импортов ([#60](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/60),
  [`7e3a138`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/7e3a138db9e6dd5e0a9bab46a1dc663ef7d25943))


## v0.6.0 (2026-02-04)

### Features

- Добавил команды для изменения ролей пользователей для админов
  ([#59](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/59),
  [`8655920`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8655920c24e6b819c566aa5850aee0a2a27c9cbe))

- Добавил функции для ручного изменения ролей
  ([#59](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/59),
  [`8655920`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8655920c24e6b819c566aa5850aee0a2a27c9cbe))

### Refactoring

- Добавил пользовательские ошибки для доменной логики, бизнес-логики и Репозиториев для повышения
  качетсва обработки ошибок ([#59](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/59),
  [`8655920`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8655920c24e6b819c566aa5850aee0a2a27c9cbe))

- Добавил пользовательские ошибки для доменной логики, бизнес-логики и Репозиториев для повышения
  качетсва обработки ошибок ([#58](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/58),
  [`2b203fa`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/2b203faf4b0240cfbbc3c042c2f761a290073e5f))

- Организация импортов ([#59](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/59),
  [`8655920`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8655920c24e6b819c566aa5850aee0a2a27c9cbe))

- Организация импортов ([#58](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/58),
  [`2b203fa`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/2b203faf4b0240cfbbc3c042c2f761a290073e5f))

- **exceptions**: Domain errors ([#58](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/58),
  [`2b203fa`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/2b203faf4b0240cfbbc3c042c2f761a290073e5f))


## v0.5.1 (2026-02-04)

### Bug Fixes

- Оканчательно ввёл gracefull shutdown при завершении работы программы.
  ([`87c5965`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/87c59650c81d1a2821a5723e43dbbe03db9dcd4c))


## v0.5.0 (2026-02-04)

### Bug Fixes

- Remove desync session ([#57](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/57),
  [`d4fdb63`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/d4fdb63381fa7c1bda8f55461aa749dea165b858))

- Исправил логику проверки ролей, добавив возможность эффективного обрабатывать множество ролей на
  одном хэндлере, диалоге ([#57](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/57),
  [`d4fdb63`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/d4fdb63381fa7c1bda8f55461aa749dea165b858))

- Исправил ошибку сравнения временных значений при обновления last active status, и убрал ранее
  сделанный хак ([#57](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/57),
  [`d4fdb63`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/d4fdb63381fa7c1bda8f55461aa749dea165b858))

- Убрал enqueue=True из логгера для исправления блокировки программы при её завершении
  ([#57](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/57),
  [`d4fdb63`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/d4fdb63381fa7c1bda8f55461aa749dea165b858))

### Features

- Добавил фильтер для conditional UI в aiogram-dialog, с добавлением списка ролей пользователя в
  данные из middleware ([#57](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/57),
  [`d4fdb63`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/d4fdb63381fa7c1bda8f55461aa749dea165b858))

### Refactoring

- Добавил VO в объекты кода, и инструменты в CI-pipeline
  ([#57](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/57),
  [`d4fdb63`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/d4fdb63381fa7c1bda8f55461aa749dea165b858))


## v0.4.0 (2026-02-04)

### Bug Fixes

- Исправил логику проверки ролей, добавив возможность эффективного обрабатывать множество ролей на
  одном хэндлере, диалоге ([#56](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/56),
  [`8c16d8a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8c16d8aaae571b437283c48b6602ad215d9837ec))

- Исправил логику проверки ролей, добавив обрабатывать множество ролей на одном элементе
  ([#56](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/56),
  [`8c16d8a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8c16d8aaae571b437283c48b6602ad215d9837ec))

- Убрал enqueue=True из логгера для исправления блокировки программы при её завершении
  ([#56](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/56),
  [`8c16d8a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8c16d8aaae571b437283c48b6602ad215d9837ec))

### Features

- Добавил фильтер для conditional UI в aiogram-dialog, с добавлением списка ролей пользователя в
  данные из middleware ([#56](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/56),
  [`8c16d8a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8c16d8aaae571b437283c48b6602ad215d9837ec))

### Refactoring

- Добавил VO в объекты кода, и инструменты в CI-pipeline
  ([#56](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/56),
  [`8c16d8a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/8c16d8aaae571b437283c48b6602ad215d9837ec))


## v0.3.0 (2026-02-04)

### Bug Fixes

- Убрал enqueue=True из логгера для исправления блокировки программы при её завершении
  ([#55](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/55),
  [`95b7928`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/95b7928d6fd6c13fbdca10ac13300f10baa58b42))

### Features

- Добавил фильтер для conditional UI в aiogram-dialog, с добавлением списка ролей пользователя в
  данные из middleware ([#55](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/55),
  [`95b7928`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/95b7928d6fd6c13fbdca10ac13300f10baa58b42))

### Refactoring

- Добавил VO в объекты кода, и инструменты в CI-pipeline
  ([#55](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/55),
  [`95b7928`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/95b7928d6fd6c13fbdca10ac13300f10baa58b42))


## v0.2.1 (2026-02-03)

### Bug Fixes

- Исправил привязку telegram id к internal id и выделил отдельный Репозиторий для работы с ролями
  ([#54](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/54),
  [`f60cb8c`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/f60cb8cac161eebac3f3e2351fd2b0eff33157cd))

- Исправил привязку telegram id к internal id и его использования для проверки роли
  ([#54](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/54),
  [`f60cb8c`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/f60cb8cac161eebac3f3e2351fd2b0eff33157cd))

- Решил проблему с учётом временных поясов
  ([#54](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/54),
  [`f60cb8c`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/f60cb8cac161eebac3f3e2351fd2b0eff33157cd))

### Refactoring

- Добавление нового репозитория и перемещение туда метода из UserRepository
  ([#54](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/54),
  [`f60cb8c`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/f60cb8cac161eebac3f3e2351fd2b0eff33157cd))


## v0.2.0 (2026-02-03)

### Bug Fixes

- Check automatic release generation
  ([`157db2b`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/157db2b25b0c63dd0ca65a6c42808b6d93b6bb8c))

- Debug release final
  ([`fc4fc56`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/fc4fc5654b77ec370c70d459d8f5277910c98453))

- Disable build command for semantic release
  ([`cd74010`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/cd740106ede62777e2d0ab63cfcf58d29025ef64))

- Final test for auto-release
  ([`68cb4f6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/68cb4f65bffea9dfd279de791f222788205899d1))

- Fix release config debug
  ([`a33d372`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a33d372e9c3c5657e229455b51bd8f5e02f2d418))

- Retry release after manual fix
  ([`234b492`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/234b49269c9baa9fd663b0961e2695c55be5e62a))

### Features

- Force new release generation
  ([`64d9179`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/64d9179c0e04c69787fdca47d7247c8788fd83d3))

- Force new release generation
  ([`662a234`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/662a2343e3ce06e86134189a4bfdfbca2e1310c5))


## v0.1.0 (2026-02-04)

### Bug Fixes

- Исправления в release ci
  ([`229526b`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/229526b213479447e4dda0e88d156aefc63ef1a2))

- Малые обновления realise pipeline
  ([`1c1e0f9`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/1c1e0f9c29079cecadb4b2c7078ed2a3061e8956))

### Features

- Initial project release
  ([`3dbe212`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/3dbe212db8293c1b24ca1f3b61ab586f4877c5c1))


## v0.0.0 (2026-02-03)

- Initial Release
