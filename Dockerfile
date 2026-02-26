FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY run.py ./
COPY alembic ./alembic
COPY alembic.ini ./
COPY fill_point_db.py ./
COPY scripts/docker-entrypoint.sh ./scripts/docker-entrypoint.sh


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=builder /app /app
RUN chmod +x /app/scripts/docker-entrypoint.sh && mkdir -p /app/data && chown -R app:app /app

USER app

CMD ["/app/scripts/docker-entrypoint.sh"]
