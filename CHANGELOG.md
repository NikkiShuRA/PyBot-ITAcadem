# CHANGELOG

<!-- version list -->

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
