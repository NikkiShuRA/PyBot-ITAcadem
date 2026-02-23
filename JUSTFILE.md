# Just Command Guide

## Install `just`

### Windows

- `winget install Casey.Just`
- or `choco install just`
- or `scoop install just`

### macOS

- `brew install just`

### Linux

- `cargo install just`
- or use your distro package manager (`apt`, `dnf`, `pacman`) if available

Check installation:

- `just --version`

## Usage

Show command list:

- `just`
- `just --list`
- `just help`

Run a command:

- `just install-dev`
- `just lint`
- `just run`

Run migration command with argument:

- `just migrate-create "add user status"`

## Commands in this project

- `help` - Show available commands
- `install` - Install production dependencies
- `install-dev` - Install all dependencies, including dev groups
- `run` - Run the bot
- `format` - Format code with ruff
- `format-check` - Check formatting with ruff
- `lint` - Run linter
- `type-check` - Run type checker (`ty`)
- `migrate-create "<msg>"` - Create Alembic migration
- `migrate-apply` - Apply all Alembic migrations
- `clean` - Remove local caches and virtualenv
- `pre-commit` - Install and run pre-commit hooks

## `just` vs `make`

- `just` is a command runner first; `make` is a build tool first.
- `just` syntax is simpler for developer tasks.
- `just` usually gives better DX for local command execution.
- `make` is commonly preinstalled on Linux/macOS, but often inconvenient on Windows.
- `just` does not rely on file timestamp build semantics; recipes run only when explicitly called.

For this project, `just` is used as a cleaner local task runner replacement for `make` workflows.
