# CHANGELOG

<!-- version list -->

## v0.29.0 (2026-04-25)

### Bug Fixes

- Исправил остаточные импорты объекта конфигурации settings вне src
  ([`0ec6cb5`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0ec6cb55df029eac382cfee50048fa4d70a6dae9))

- **bot**: Уточняет запуск polling и уведомление о старте
  ([`71a2581`](https://github.com/Cewerty/PyBot-ITAcadem/commit/71a2581fe0eab2331b553d9a6cac2d770c1ad86e))

- **db**: Откладывает чтение настроек базы данных до запуска
  ([`9797f5a`](https://github.com/Cewerty/PyBot-ITAcadem/commit/9797f5a75bf2bc7362071656a220f9eb9a8ff0d1))

- **deploy**: Обновляет entrypoint Health API в Compose
  ([`f592f9d`](https://github.com/Cewerty/PyBot-ITAcadem/commit/f592f9ddc52615ae03997c05a0f19d21b376d70a))

### Build System

- **deps**: Добавляет asyncpg для работы с PostgreSQL
  ([`b84516a`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b84516a19f2f78aea2331ce03896b95cd10e76a0))

### Chores

- **deps**: Добавил httpx для fastapi идиоматичного тестирования
  ([`77926c7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/77926c79c0032eef80af2fd92afbd63602b521db))

- **deps**: Изменения в зависимостях
  ([`1299158`](https://github.com/Cewerty/PyBot-ITAcadem/commit/12991584cfdbecc874ea3820089d07fd3dd4add4))

- **docs**: Добавил docstrings в utils для автогенерируемой документации
  ([`8768c3f`](https://github.com/Cewerty/PyBot-ITAcadem/commit/8768c3f3881bb1ef6d4bdff8538fa7f777330391))

- **docs**: Добавил docstrings в формате google style guide для элементов health api
  ([`c92e13c`](https://github.com/Cewerty/PyBot-ITAcadem/commit/c92e13c4781f4e80d2e332e1adc58ad46ecbb493))

- **docs**: Добавил docstrings для application services
  ([`2a7de40`](https://github.com/Cewerty/PyBot-ITAcadem/commit/2a7de40f31c6ec72a58178acf573c364f16f3799))

- **docs**: Добавил docstrings для DB элементов
  ([`c8653f3`](https://github.com/Cewerty/PyBot-ITAcadem/commit/c8653f384e1c71b6a161e4c2a890e56b20d76395))

- **docs**: Добавил docstrings для константовых ENUMS
  ([`2418d53`](https://github.com/Cewerty/PyBot-ITAcadem/commit/2418d5394544db04ad4d0d07656f270fe800a3d0))

- **docs**: Добавил docstrings для публичных элементов системы
  ([`e44bddf`](https://github.com/Cewerty/PyBot-ITAcadem/commit/e44bddf5a759d3f0f8573dfbd1f61a9ff7db494a))

- **docs**: Добавил docstrings для Репозиториев
  ([`e09a823`](https://github.com/Cewerty/PyBot-ITAcadem/commit/e09a8237cbf5748bc29c8cac4e06e81cfc8af7f0))

- **docs**: Зафиксировал изменения по переходу к process type от spawn
  ([`f5a9fb2`](https://github.com/Cewerty/PyBot-ITAcadem/commit/f5a9fb261819a335ecfae8c781c44c44e0ee28e9))

- **lock**: Синхронизирует формат lock-файла
  ([`aa3f3e7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/aa3f3e771fa4f9eff381199596b6196096bc27d9))

- **test**: Добавил новые тесты под важные use case в health api
  ([`bc80c5d`](https://github.com/Cewerty/PyBot-ITAcadem/commit/bc80c5d71ac37cd333b5bc6cfa7c6ed9bc9da725))

- **test**: Добавил тестов для важных admin-flow и подкорректировал общую конфигурацию для тестов
  ([`ed33c90`](https://github.com/Cewerty/PyBot-ITAcadem/commit/ed33c90cf5e21ab16a90fb73c87a6fbabc016601))

### Code Style

- **config**: Форматирует валидатор числа TaskIQ-воркеров
  ([`891bdcf`](https://github.com/Cewerty/PyBot-ITAcadem/commit/891bdcf70ca063de6858478741a47749741a2d0c))

### Documentation

- **bot**: Обновляет правила размещения Telegram-слоя
  ([`ec0a964`](https://github.com/Cewerty/PyBot-ITAcadem/commit/ec0a9647965ef7d2ab7127538dd13ef385dbed0c))

- **health**: Обновляет путь Health API в документации
  ([`1e6f247`](https://github.com/Cewerty/PyBot-ITAcadem/commit/1e6f2477d8954d3aae54c5e14a3c8af1c415bc08))

### Features

- Add runtime logging and taskiq config guards
  ([`9b361a8`](https://github.com/Cewerty/PyBot-ITAcadem/commit/9b361a8e6d1839e8a156d9296935a2a6053a2945))

- Implement health probe infrastructure and service updates
  ([`6535f2e`](https://github.com/Cewerty/PyBot-ITAcadem/commit/6535f2e82a7679912eb34ac2b5cb6cd1130f4599))

- Ввёл базис для process type разделения в проекте
  ([`d0ed430`](https://github.com/Cewerty/PyBot-ITAcadem/commit/d0ed430259df22853b4829a17eba87d2a7e6e078))

- **deploy**: Полноценно разделил process для запуска бота и для запуска health api, также изменил
  под это docker
  ([`bdd3be9`](https://github.com/Cewerty/PyBot-ITAcadem/commit/bdd3be9bf1f1dff5cb52231293b3a3e96c34f8d0))

### Refactoring

- Move bot texts into presentation layer
  ([`ae2f1b6`](https://github.com/Cewerty/PyBot-ITAcadem/commit/ae2f1b6d31938740831f1dbcfe632a035b56b427))

- Обновил тест под process type формат run.py
  ([`80235ab`](https://github.com/Cewerty/PyBot-ITAcadem/commit/80235ab028523f62b82e2b560d1f99638c21bccd))

- Убрал deprecated метод и файл с ним, который нужен был для старого run.py
  ([`d0db185`](https://github.com/Cewerty/PyBot-ITAcadem/commit/d0db185c6fc9986974c5c461b34f20a8c1353862))

- Удалил старый shim для health api
  ([`5704fcc`](https://github.com/Cewerty/PyBot-ITAcadem/commit/5704fcc12ddfadb6fb2641bfb7e72305f7f0f6f2))

- **bot**: Переносит Telegram-слой в presentation
  ([`f85a386`](https://github.com/Cewerty/PyBot-ITAcadem/commit/f85a3861121e40134be2e2b26a5f9b68ec19e66d))

- **health**: Переносит Health API в web presentation
  ([`4568904`](https://github.com/Cewerty/PyBot-ITAcadem/commit/4568904de97f765df5a9c0c68c420a2e757a6b51))


## v0.28.0 (2026-04-22)

### Bug Fixes

- Исправил битую первую строку
  ([`da60bf4`](https://github.com/Cewerty/PyBot-ITAcadem/commit/da60bf4076fe037f0872203b6ce99e8083f7ee6b))

### Chores

- **test**: Добавил тесты для изменений в di-контейнерах и зависимостях в них
  ([`ad642cc`](https://github.com/Cewerty/PyBot-ITAcadem/commit/ad642ccfe3d484be44a7ff2646cfc7625ba30e6e))

### Features

- Довершил ввод .env-конфигурируемой системы role policy без создания import-time side effect
  ([`fab7634`](https://github.com/Cewerty/PyBot-ITAcadem/commit/fab7634c1baa16ce710055b766cd907367f391e8))

### Refactoring

- Внедрить BotSettings в сервисы и адаптеры
  ([`7f6cbee`](https://github.com/Cewerty/PyBot-ITAcadem/commit/7f6cbeed982cc42f7427e27ca57bcc5f3b612911))

- Изменил логику middelware, чтобы она поддерживала role policy без создания side-effect при
  импортировании конфигурации
  ([`d9037f1`](https://github.com/Cewerty/PyBot-ITAcadem/commit/d9037f1b5c56384a9a77ad38f58799c6f86c7ed9))

- Передавать BotSettings в runtime бота и middleware
  ([`3d2c7ab`](https://github.com/Cewerty/PyBot-ITAcadem/commit/3d2c7ab342395aeee430580524fd49c080092496))

- Перенёс создание DB engine на конфигурацию из DI-контейнера
  ([`b311799`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b3117990a10a9954e3e71cd1e9bd0a2401728a43))

- Сделать явную регистрацию TaskIQ задач
  ([`3dc109e`](https://github.com/Cewerty/PyBot-ITAcadem/commit/3dc109e9c9e4ee1ec57ee70795678aa8232db1e5))

### Testing

- Migrate settings usage to isolated settings_obj fixture
  ([`8c4ac9f`](https://github.com/Cewerty/PyBot-ITAcadem/commit/8c4ac9fa2d3149ceb63a81dfda9154c62d009165))


## v0.27.0 (2026-04-19)

### Bug Fixes

- Resolve Ruff E402 and F821 typing issues in config.py
  ([`b3dc264`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b3dc26403453674be26c08fd36efc2de394fdcc1))

- Исправил автоматическую подгрузку .env в скрипте заполнения БД
  ([`ea5d2a2`](https://github.com/Cewerty/PyBot-ITAcadem/commit/ea5d2a2a858743c133e0c6cd7c5767bada33d704))

- Исправил конфигурацию тестов, для того чтобы тесты не читали объект конфигурации до запуска
  фикстур
  ([`7cceb66`](https://github.com/Cewerty/PyBot-ITAcadem/commit/7cceb66b75d095f4e74f728df1fdd82da652a2fb))

- Исправил ошибки в текста и убрал лишний github action
  ([`76996c0`](https://github.com/Cewerty/PyBot-ITAcadem/commit/76996c0481c51b8af167a6491a6c5a4f24bbb8ab))

- Исправил ошибку с обработкой .env при pybot-seed
  ([`f5cdb72`](https://github.com/Cewerty/PyBot-ITAcadem/commit/f5cdb724bd6c1003bc5e820420f664fc5b242ddd))

- Исправил создание экземпляра движка БД
  ([`9a2ad1f`](https://github.com/Cewerty/PyBot-ITAcadem/commit/9a2ad1f35ee640f33d5af29a1a5318349fbb6136))

- **test**: Support monkeypatching config properties on SettingsProxy
  ([`ac9fc9c`](https://github.com/Cewerty/PyBot-ITAcadem/commit/ac9fc9c0c409294233a1e13102acaaf8efea6344))

### Build System

- Move faker to dev dependencies and enable hatchling packaging
  ([`646eb4f`](https://github.com/Cewerty/PyBot-ITAcadem/commit/646eb4faa72471c1e20c16212493a012e9528d72))

### Continuous Integration

- **docker**: Align local docker-compose with production and extract migrate service
  ([`ad7508f`](https://github.com/Cewerty/PyBot-ITAcadem/commit/ad7508f4e00380bc81c11b348ed8b49194c5ddad))

- **docker**: Handle graceful shutdown in entrypoint and apply explicit project installation
  ([`6f6eab3`](https://github.com/Cewerty/PyBot-ITAcadem/commit/6f6eab31747b8ef50f44e514501139938875bb24))

### Documentation

- **architecture**: Document SQLite bottlenecks, rate limit design, and health API ADR
  ([`beede99`](https://github.com/Cewerty/PyBot-ITAcadem/commit/beede997b33fe6a13df70f494e1faa02b4babd56))

### Features

- **config**: Wrap settings instantiation in lru_cache for testability
  ([`3bcabd0`](https://github.com/Cewerty/PyBot-ITAcadem/commit/3bcabd06e83fd6953770fb23847d9f45b55054fc))

- **logging**: Support structured JSON log format and tracing
  ([`c7e920c`](https://github.com/Cewerty/PyBot-ITAcadem/commit/c7e920cc0024a0131614299956b060189a56944b))

### Refactoring

- Убрал лишний прокси класс вокруг кэшированной функции-фабрики объекта конфигурации
  ([`7bec899`](https://github.com/Cewerty/PyBot-ITAcadem/commit/7bec899b8364d6d21e30166ad2f72c07117f04ae))

- **cli**: Move seed script to cli module and configure entrypoint
  ([`2fcd049`](https://github.com/Cewerty/PyBot-ITAcadem/commit/2fcd049fdb2381605bb1eb0103ddeef16db1c750))


## v0.26.1 (2026-04-19)

### Bug Fixes

- Исправил логику с инвертированной тернарной логикой внутри application service, проверки None в
  Middelware проверки ролей и обновил тесты под новые use case в UserService.
  ([`6418ed2`](https://github.com/Cewerty/PyBot-ITAcadem/commit/6418ed2d924e5d0198782abd30d4b8522d896d0f))

### Build System

- Configure tach architecture linter
  ([`d944e62`](https://github.com/Cewerty/PyBot-ITAcadem/commit/d944e6260dbb0933d9c8f8668a3fd1ce805578bd))

- **deps**: Install tach linter dependency
  ([`714ca02`](https://github.com/Cewerty/PyBot-ITAcadem/commit/714ca020d1dbcb86e6c0d1246ca48515751a2b96))

### Refactoring

- **arch**: Resolve architectural violations for tach
  ([`8e138cb`](https://github.com/Cewerty/PyBot-ITAcadem/commit/8e138cbe2544e68c33d0a6fa057eddaa8086dc44))


## v0.26.0 (2026-04-18)

### Bug Fixes

- **leaderboard**: Show week period when sections are empty
  ([`c369399`](https://github.com/Cewerty/PyBot-ITAcadem/commit/c36939940ee1f72c5b60833432961c41475ff4a8))

### Chores

- **lockfile**: Bump workspace package version to 0.25.0
  ([`5aed622`](https://github.com/Cewerty/PyBot-ITAcadem/commit/5aed622b15f2d620178d6fdef16e9900f8467967))

### Features

- **taskiq**: Configure weekly leaderboard retry policy
  ([`ce78b0c`](https://github.com/Cewerty/PyBot-ITAcadem/commit/ce78b0c4f5350cf38ec6875067a9a27af0cc51e7))


## v0.25.0 (2026-04-18)

### Bug Fixes

- Исправил бизнес-логику лидерборда на учитывание только повышения очков, а не изменения очков в
  целом
  ([`0047f7a`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0047f7a037bb94e98368a8922488c63a356b9b64))

- **leaderboard**: Apply net weekly delta and tz-aware period
  ([`4166a58`](https://github.com/Cewerty/PyBot-ITAcadem/commit/4166a58c557cad8451ad33a840418f86d78807a0))

### Features

- Weekly leaderboard publishing via taskiq
  ([`62227cf`](https://github.com/Cewerty/PyBot-ITAcadem/commit/62227cf3c771d62b46c12c7f7438ac639b9e8ab9))

- Добавил команду для получения id чата для удобного получения id для еженедельной рассылки и прочих
  рассылок по времени в определённый чат
  ([`87b6347`](https://github.com/Cewerty/PyBot-ITAcadem/commit/87b6347b9064599779bd0500110dc28bc7cd6fcc))

### Refactoring

- **taskiq**: Extract weekly leaderboard schedule wiring
  ([`2df7e12`](https://github.com/Cewerty/PyBot-ITAcadem/commit/2df7e12989c88ceb406f73a68067d864fd8da088))


## v0.24.0 (2026-04-11)

### Bug Fixes

- Включил html-рендеринг профиля и ошибку регистрации
  ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- Включил sqlite foreign keys в runtime ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- Исправил выборку пользователей по роли ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- Исправил реггрессию в тестах с healthAPI
  ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- Исправлеине реггрессий в валидации ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- Обработал ожидаемые ошибки рассылки ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- Скрываю детали readiness ошибки базы ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- Убрал текст из callback role request ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- **ci/cd**: Добавил параметр для перехода к современному node.js для устранения warning при запуске
  Github actions ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- **docs**: Добавил .gitkeep для overrides
  ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

### Chores

- **docs**: Изменение в настройках MK Doc Material и небольшие правки в тесте
  ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

### Features

- Добавил журнал транзакций баллов ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- Добавил команду leaderboard ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

- Добавил просмотр каталога и ролей пользователя
  ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))

### Refactoring

- Упростил async-конфиг alembic ([#90](https://github.com/Cewerty/PyBot-ITAcadem/pull/90),
  [`b4fb5f7`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b4fb5f7d328f83a2c11c903edeeebe71539765b4))


## v0.23.0 (2026-04-11)

### Bug Fixes

- Включил html-рендеринг профиля и ошибку регистрации
  ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- Включил sqlite foreign keys в runtime ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- Исправил выборку пользователей по роли ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- Исправил реггрессию в тестах с healthAPI
  ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- Исправлеине реггрессий в валидации ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- Обработал ожидаемые ошибки рассылки ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- Скрываю детали readiness ошибки базы ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- Убрал текст из callback role request ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- **ci/cd**: Добавил параметр для перехода к современному node.js для устранения warning при запуске
  Github actions ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- **docs**: Добавил .gitkeep для overrides
  ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

### Chores

- **docs**: Изменение в настройках MK Doc Material и небольшие правки в тесте
  ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

### Features

- Добавил журнал транзакций баллов ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- Добавил команду leaderboard ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- Добавил просмотр каталога и ролей пользователя
  ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

### Performance Improvements

- Оптимизация кэширования слоев и времени сборки Dockerfile
  ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

- Улучшил кэшировние в Dockerfile для ускорения деплоя системы на VDS
  ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))

### Refactoring

- Упростил async-конфиг alembic ([#89](https://github.com/Cewerty/PyBot-ITAcadem/pull/89),
  [`0988b09`](https://github.com/Cewerty/PyBot-ITAcadem/commit/0988b0976ecd931511cbdd00f98c431fc4aa06dd))


## v0.22.1 (2026-04-11)


## v0.22.0 (2026-04-11)

### Bug Fixes

- Включил html-рендеринг профиля и ошибку регистрации
  ([`e94a740`](https://github.com/Cewerty/PyBot-ITAcadem/commit/e94a7406c4d0c23941eef3d5d605f7f5a439c2cb))

- Включил sqlite foreign keys в runtime
  ([`a6d7373`](https://github.com/Cewerty/PyBot-ITAcadem/commit/a6d7373df58eb380da332ae028f1ecd37aca2595))

- Исправил выборку пользователей по роли
  ([`8a79496`](https://github.com/Cewerty/PyBot-ITAcadem/commit/8a79496b403271c59de95057f31dfc7d3b336ee9))

- Исправил реггрессию в тестах с healthAPI
  ([`aebfdc8`](https://github.com/Cewerty/PyBot-ITAcadem/commit/aebfdc8baf63f993d9614aa2c1722a51a75d597e))

- Исправлеине реггрессий в валидации
  ([`d9c8c6e`](https://github.com/Cewerty/PyBot-ITAcadem/commit/d9c8c6e279102d8e531fdc0fc86511f4605b4aa0))

- Обработал ожидаемые ошибки рассылки
  ([`44e88d8`](https://github.com/Cewerty/PyBot-ITAcadem/commit/44e88d82bb94b5132f4cac6141209e2907757e74))

- Скрываю детали readiness ошибки базы
  ([`485b227`](https://github.com/Cewerty/PyBot-ITAcadem/commit/485b227ea7d6f889427c8b9631b82cac137268ea))

- Убрал текст из callback role request
  ([`2889692`](https://github.com/Cewerty/PyBot-ITAcadem/commit/28896922f9117487b2e2b77e576e58358132fd5b))

- **docs**: Добавил .gitkeep для overrides
  ([`9c80d75`](https://github.com/Cewerty/PyBot-ITAcadem/commit/9c80d750004661332b66b6191cd9381684077a8e))

### Chores

- **docs**: Изменение в настройках MK Doc Material и небольшие правки в тесте
  ([`b73da48`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b73da48a3e8d49e35162e9da78a1ea96e422afe9))

### Features

- Добавил журнал транзакций баллов
  ([`cd899ce`](https://github.com/Cewerty/PyBot-ITAcadem/commit/cd899ce6bbca3c60aa7126127b8a1dcd21426d9e))

- Добавил команду leaderboard
  ([`1b9ebf1`](https://github.com/Cewerty/PyBot-ITAcadem/commit/1b9ebf10d156370cc630322533b9ea922f0f2492))

- Добавил просмотр каталога и ролей пользователя
  ([`95f89bf`](https://github.com/Cewerty/PyBot-ITAcadem/commit/95f89bfa2601d43e654661e47d529b49b34bac76))

### Refactoring

- Упростил async-конфиг alembic
  ([`b680b36`](https://github.com/Cewerty/PyBot-ITAcadem/commit/b680b3668e74fdcdf582a7ee9841f0c78a98f7de))


## v0.21.0 (2026-04-03)

### Bug Fixes

- Включил html-рендеринг профиля и ошибку регистрации
  ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

- Включил sqlite foreign keys в runtime
  ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

- Исправил выборку пользователей по роли
  ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

- Исправил реггрессию в тестах с healthAPI
  ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

- Исправлеине реггрессий в валидации ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

- Обработал ожидаемые ошибки рассылки ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

- Скрываю детали readiness ошибки базы ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

- Убрал текст из callback role request ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

### Features

- Добавил журнал транзакций баллов ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

- Добавил команду leaderboard ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

- Добавил просмотр каталога и ролей пользователя
  ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))

### Refactoring

- Упростил async-конфиг alembic ([#87](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/87),
  [`b75db3a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/b75db3a78517257b00fffabe5a706c79bcd0d531))


## v0.20.0 (2026-04-01)

### Features

- Добавил runtime alerts для lifecycle бота
  ([`4ab568b`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/4ab568b9f50c9a6af5cfc80f5fba372f543df5d5))

### Refactoring

- Упростил сборку текста профиля
  ([`4c0e54d`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/4c0e54dd7ed2e64dbc84a407671e40a6f5ad1900))


## v0.19.0 (2026-03-27)

### Bug Fixes

- Regenerate uv lock after docs cherry-pick
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- Улучшил ответы команд и role request flow
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- **seed**: Убрал слишком общие типы в seed-скрипте
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

### Chores

- **docs**: Добавил MK Doc Material документацию к проекту
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- **lock**: Обновил uv.lock ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

### Documentation

- **architecture**: Зафиксировал ADR для runtime и интеграций
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

### Features

- Добавил поддержку proxy для Telegram Bot API
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- Улучшить UX бота, регистрацию и документацию проекта
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- **UI**: Добавил util-функцию для создания вечных html-ссылок в telegram
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- **UI**: Привёл весь текст в системе тг-бота к единому стилю и выделил слой текстов
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

### Refactoring

- Добавил обозначение шагов в регистрацию
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- Небольшие изменения в текстовом слое ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- Удалил ненужный движок для генерации асинхронных сессий.
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- Улучшил вывод /help в лс ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- Улучшил отображение админских и нет команд в /help
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- **core**: Переименовал типы баллов и обновил пользовательские сценарии
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- **user-activity**: Перенёс трекинг активности пользователя в сервисный слой
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))

- **user-services**: Декомпозировал сервисы пользователей и связанные сценарии
  ([#86](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/86),
  [`92becac`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/92becaca1a7f1bddea5c3b3d0cf7ca6c80cf3ca7))


## v0.18.1 (2026-03-19)

### Bug Fixes

- **seed**: Пофиксил ошибку с конфигурацией seed-скрипта с tyro cli
  ([`29d5736`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/29d57363ad374420bad4e0ec9fe49979a947b4b4))


## v0.18.0 (2026-03-19)

### Bug Fixes

- **points**: Валидировал начисления через Points
  ([`d0305d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/d0305d6aef74eb496fb01b8f7cf3cd4e65d140ee))

### Chores

- **deploy**: Harden ci and production rollout
  ([`3897628`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/38976289df1813b5add7f5b230fb965cbb227bac))

- **deployment**: Добавил базовую runtime-валидацию для деплоя на VDS
  ([`03d8be8`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/03d8be8542bf1d7138b3f3b907d74214fd87fd97))

### Documentation

- **project**: Refresh onboarding and security guides
  ([`c39d47a`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/c39d47a65af42bf5750376fc22c12f27b5377db5))

### Features

- **profile**: Добавил welcome-шаг регистрации
  ([`d0227f7`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/d0227f776256eb68de28840ca09b3bcf34078195))

- **seed**: Add configurable fill-point-db cli
  ([`9ab684e`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/9ab684e6061dfa1b2f090ce973e0f347f9d2fd75))

### Refactoring

- **logging**: Унифицировал runtime-логи бота и taskiq
  ([`a33e709`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/a33e7092c3f9fc0d895e7afc1c40a8d92db31f32))


## v0.17.4 (2026-03-18)


## v0.17.3 (2026-03-17)


## v0.17.2 (2026-03-17)

### Bug Fixes

- Исправил некорректную финальную проверку на работоспособность docker compose
  ([`dbd8b2c`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/dbd8b2c293e13d704dd2d23efbc74499178fa7b2))

### Chores

- **deployment**: Добавил изменения под автоматизированный деплой на выделенный VDS
  ([`70047af`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/70047af642df234a5112a7a03fe336c5e5aae0c9))

- **deployment**: Добавил изменения под автоматизированный деплой на выделенный VDS
  ([#85](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/85),
  [`9984f01`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/9984f0164992ed2f1631e68cdc6cfafac9480721))


## v0.17.1 (2026-03-16)

### Bug Fixes

- Исправил ошибку импорта DTO в логику профиля
  ([`68dde53`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/68dde532f76b6d97e03287cc0a99519f7a9f6500))


## v0.17.0 (2026-03-16)

### Bug Fixes

- Изменить проблемы с версией uv ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))

- Исправил логику теста ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))

- Исправил ошибки в зависимостях в uv.lock
  ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))

- Исправил ошибочные тесты, а также убрал последствия неверного следа при фиксах, связанные с
  версией uv ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))

- Исправление проблем с uv, которые ломают CI-pipeline
  ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))

### Chores

- **deployment**: Повысил безопасность локального делпоя, а также начал делать фундамент для
  автоматизированного деплоя на внешний сервер
  ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))

- **test**: Добавил тесты для важных handler-ов aiogram, и элементов aiogram-dialog
  ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))

### Features

- Добавил production-деплой и улучшил сервисные сценарии бота
  ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))

### Refactoring

- Исправил интерфейс в сервисах User-а, чтобы это лучше отражало их реальное поведение, также создал
  ADR по этому процессу, и обновил тесты
  ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))

- Отрефакторил логику профиля, seed-скрипт, уровней и логики баллов, а также добавил кэширование для
  pure f(x) ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))

- Улучшил UserService и добавил Domain Errors
  ([#83](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/83),
  [`10738d6`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/10738d6e7757c9859d8b5f1ae2d402dbd0d47b78))


## v0.16.1 (2026-03-15)

### Bug Fixes

- Исправил логику теста ([#82](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/82),
  [`69679fa`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/69679fa1e271bfc5595ceb3d63a594339da4ff5e))

### Refactoring

- Выделение профильного сервиса и выравнивание контрактов lookup
  ([#82](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/82),
  [`69679fa`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/69679fa1e271bfc5595ceb3d63a594339da4ff5e))

- Исправил интерфейс в сервисах User-а, чтобы это лучше отражало их реальное поведение, также создал
  ADR по этому процессу, и обновил тесты
  ([#82](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/82),
  [`69679fa`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/69679fa1e271bfc5595ceb3d63a594339da4ff5e))

- Отрефакторил логику профиля, seed-скрипт, уровней и логики баллов, а также добавил кэширование для
  pure f(x) ([#82](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/82),
  [`69679fa`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/69679fa1e271bfc5595ceb3d63a594339da4ff5e))

- Улучшил UserService и добавил Domain Errors
  ([#82](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/82),
  [`69679fa`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/69679fa1e271bfc5595ceb3d63a594339da4ff5e))


## v0.16.0 (2026-03-12)

### Bug Fixes

- Исправил ошибку конфигурации, через создания подкласса с отдельными настройками проставленными на
  локальные настройки для теста ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

- Исправил ошибку с абсолютным путём до события
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

- Исправил прямую зависимость теста от .env
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

- Полностью убрал прямую работу с нулевым значением поля для id админа для запроса к нему
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

- Убрал временное значение по-умолчанию для поля admin telegram id
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

### Chores

- **style**: Использование форматера на пропущенных pre-commit-hook-ом ошибок
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

- **tests**: Добавил тесты к логике фонового оповещения
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

### Features

- Добавил отправку оповещений пользователю, которому было назначены очки
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

- Создал ядро работы с очередями и фоновыми задачами через неё
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

### Refactoring

- Введение TaskIQ notification выполнения and рефакторинг broadcast flow
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

- Выделение валидации в отдельные DTO для усиления контракта данных
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

- Добавил domain errors и улучшил обработку неожиданных ошибок при работе программы, добавил новые
  DTO для инкапсуляции валидации и упрочнения контракта данных, а также удалил дублирование при
  проверке типа TaskSchedule, изменил тесты под новые сигнатуры методов и функций, учитывающие новые
  DTO ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))

- Добавил DTO для фоновой задачи оповещения и перенёс туда валидацию входящих в задачу данных
  ([#81](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/81),
  [`e45eb50`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/e45eb50b75372d556088b69065af750a185c311e))


## v0.15.1 (2026-03-03)

### Bug Fixes

- Исправил ошибку конфигурации, через создания подкласса с отдельными настройками проставленными на
  локальные настройки для теста ([#74](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/74),
  [`43019e5`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/43019e51af4c8029253bd7dca5ef4ada4e1cd74c))

- Исправил прямую зависимость теста от .env
  ([#74](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/74),
  [`43019e5`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/43019e51af4c8029253bd7dca5ef4ada4e1cd74c))

- Полностью убрал прямую работу с нулевым значением поля для id админа для запроса к нему
  ([#74](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/74),
  [`43019e5`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/43019e51af4c8029253bd7dca5ef4ada4e1cd74c))

- Убрал временное значение по-умолчанию для поля admin telegram id
  ([#74](https://github.com/NikkiShuRA/PyBot-ITAcadem/pull/74),
  [`43019e5`](https://github.com/NikkiShuRA/PyBot-ITAcadem/commit/43019e51af4c8029253bd7dca5ef4ada4e1cd74c))


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
