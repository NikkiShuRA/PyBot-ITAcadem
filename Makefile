.PHONY: help install install-dev run format format-check lint type-check migrate-create migrate-apply

# Цвета для вывода
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

help: ## Показать эту справку
	@echo ''
	@echo 'Доступные команды:'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''

install: ## Установить основные зависимости (production)
	uv sync

install-dev: ## Установить все зависимости включая dev-группу (alembic, ruff, ty и т.д.)
	uv sync --all-groups

run: ## Запустить бота
	uv run run.py

format: ## Форматировать код через ruff
	uv run ruff format .

format-check: ## Проверить форматирование кода через ruff
	uv run ruff format --check --diff .

lint: ## Линтинг через ruff
	uv run ruff check .

type-check: ## Проверка типов через ty (как в pre-commit)
	uv run ty check --python=.venv/ --output-format github --target-version 3.12 src/

migrate-create: ## Создать новую миграцию Alembic (пример: make migrate-create msg="add new column")
	@if [ -z "$(msg)" ]; then \
		echo "$(YELLOW)Ошибка: укажите сообщение миграции через msg=\"описание\"$(RESET)"; \
		exit 1; \
	fi
	uv run alembic revision --autogenerate -m "$(msg)"

migrate-apply: ## Применить все миграции (upgrade head)
	uv run alembic upgrade head

clean: ## Очистить кэши Python и uv
	rm -rf .venv __pycache__ */__pycache__ .ruff_cache .mypy_cache
	uv cache clean

pre-commit: install-dev ## Установить и запустить pre-commit (один раз)
	uv run pre-commit install
	uv run pre-commit run --all-files
