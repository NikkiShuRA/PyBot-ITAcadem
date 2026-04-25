# --- Stage 1: install dependencies into a virtual-env -----------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv

WORKDIR /app

# 1. Lock-файлы копируются первыми — слой инвалидируется
#    ТОЛЬКО при изменении зависимостей, не кода.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2. Исходный код и runtime-файлы копируются отдельным слоем.
COPY src ./src
COPY README.md ./
COPY run.py ./
COPY fill_point_db.py ./
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts/docker-entrypoint.sh ./scripts/docker-entrypoint.sh

# 2.1 Инсталлируем сам проект (создает исполняемый файл pybot-seed и добавляет src в sys.path)
RUN uv sync --frozen --no-dev

# --- Stage 2: lean runtime image -------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

# 3. venv копируется отдельно от кода — при изменении только кода
#    этот слой остаётся закэшированным.
COPY --from=builder /app/.venv /app/.venv

# 4. Application code и runtime-файлы.
COPY --from=builder /app/src /app/src
COPY --from=builder /app/run.py /app/run.py
COPY --from=builder /app/fill_point_db.py /app/fill_point_db.py
COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/scripts /app/scripts

RUN chmod +x /app/scripts/docker-entrypoint.sh && mkdir -p /app/data && chown -R app:app /app

USER app

CMD ["/app/scripts/docker-entrypoint.sh"]
