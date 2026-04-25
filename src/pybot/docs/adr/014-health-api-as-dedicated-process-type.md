# ADR 0014: Health API как отдельный process type через Docker Compose и Uvicorn

## Дата: 23-04-2026

## Статус: Accepted

## Контекст

Ранее health/readiness API поднимался как дочерний процесс внутри `run.py` (см. ADR 012). Эта схема помогла быстро запустить probes, но перестала соответствовать текущему runtime-контракту проекта:

- `run.py` теперь отвечает только за bot runtime;
- health API должен запускаться как отдельный process type по 12-Factor Factor VI (Processes);
- orchestration уже строится вокруг `docker-compose` и profile-based управления runtime-компонентами;
- для health процесса нужен отдельный управляемый запуск через ASGI-сервер.

В результате документация должна зафиксировать фактическое состояние: health больше не является spawned subprocess внутри bot-контейнера.

## Решение

Принято решение запускать **Health API как отдельный process type `health` в Docker Compose**, используя `uvicorn src.pybot.presentation.web:app`.

### Детали реализации

1. `run.py` запускает только bot runtime (`tg_bot_main`) и не управляет lifecycle health API.
2. Health API имеет отдельный composition root в `src.pybot.presentation.web:app`.
3. В `docker-compose.yml` и `docker-compose.prod.yml` добавлен сервис `health`:
   - команда запуска: `uvicorn src.pybot.presentation.web:app`;
   - host/port задаются через `HEALTH_API_HOST` и `HEALTH_API_PORT`;
   - запуск контролируется через профиль `health`.
4. Переменная `HEALTH_API_ENABLED` используется как orchestration-флаг:
   - при `true` deploy включает профиль `health` и поднимает `pybot-health`;
   - bot-сервис принудительно стартует с `HEALTH_API_ENABLED=false`, чтобы исключить двойной запуск.
5. Post-deploy smoke-check проверяет readiness health API только если процесс включен.

```text
Process types:
- bot -> python run.py
- taskiq-worker -> taskiq worker ...
- taskiq-scheduler -> taskiq scheduler ...
- health -> uvicorn src.pybot.presentation.web:app
```

## Альтернативы

* **Оставить старую схему со spawn внутри `run.py`:**
  * *Плюсы:* меньше compose-настроек и меньше runtime-сервисов.
  * *Минусы:* два процесса в одном контейнере, сложнее lifecycle/signal management, слабее соответствие 12-Factor process model.

* **Запускать health всегда без profile/feature flag:**
  * *Плюсы:* проще operational сценарий, меньше условий в оркестрации.
  * *Минусы:* меньше гибкости для окружений, где отдельный health-процесс не нужен.

* **Использовать FastAPI CLI вместо `uvicorn`:**
  * *Плюсы:* единый CLI от фреймворка.
  * *Минусы:* меньше явного контроля и предсказуемости в уже используемом ASGI runtime-контуре; `uvicorn` уже стандартен в проекте.

## Последствия

### Положительные

* [+] Health API стал полноценным отдельным process type без скрытого subprocess-менеджмента в bot runtime.
* [+] Поведение runtime проще объяснить и эксплуатировать: каждый process type имеет явный entrypoint.
* [+] Улучшено соответствие 12-Factor подходу по процессам и orchestration через compose.
* [+] Проще масштабировать и наблюдать health-процесс отдельно от bot/worker/scheduler.

### Отрицательные

* [-] Появляется дополнительный сервис в compose и дополнительная конфигурация profile/flags.
* [-] Нужна согласованность между `.env`, compose и deploy-оркестрацией.
* [-] Для локального запуска health теперь требуется явное включение профиля `health`.

## Ссылки

* [ADR 0012: Управление процессом Health API в рамках Splitted Monolith (deprecated)](012-health-api-as-spawned-process.md)
* [README.md](../../../../README.md)
* [DEPLOYMENT.md](../../../../DEPLOYMENT.md)
* [docker-compose.yml](../../../../docker-compose.yml)
* [docker-compose.prod.yml](../../../../docker-compose.prod.yml)
* [run.py](../../../../run.py)
* [src/pybot/presentation/web/health/main.py](../../presentation/web/health/main.py)
