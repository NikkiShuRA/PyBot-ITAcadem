# CHANGELOG

<!-- version list -->

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
