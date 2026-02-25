set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

default:
    @just --list

help: # Show available commands
    @just --list

install: # Install production dependencies
    uv sync

install-dev: # Install all dependencies, including dev groups
    uv sync --all-groups

run: # Run the bot
    uv run run.py

format: # Format code with ruff
    uv run ruff format .

format-check: # Check formatting with ruff
    uv run ruff format --check --diff .

lint: # Run linter
    uv run ruff check .

style: # Run formatting check and lint and type check
    just format-check
    just lint
    just type-check

type-check: # Run type checker (ty)
    uv run ty check --python=.venv/ --output-format github --target-version 3.12 src/

test-coverage: # Run tests with coverage and show missing lines
    uv run pytest --cov=src/pybot --cov-report=term-missing --cov-report=xml

migrate-create msg: # Create Alembic migration: just migrate-create "add new column"
    uv run alembic revision --autogenerate -m "{{msg}}"

migrate-apply: # Apply all Alembic migrations
    uv run alembic upgrade head

clean: # Remove local caches and venv
    uv run python -c "from pathlib import Path; import shutil; [shutil.rmtree(p, ignore_errors=True) for p in [Path('.venv'), Path('.ruff_cache'), Path('.mypy_cache'), Path('.pytest_cache')]]; [shutil.rmtree(p, ignore_errors=True) for p in Path('.').rglob('__pycache__')]"
    uv cache clean

pre-commit: # Install and run pre-commit hooks
    uv sync --all-groups
    uv run pre-commit install
    uv run pre-commit run --all-files
