# Deployment

This repository now includes a production deployment skeleton that extends the existing CI without changing the current `CI - Code Quality` or `Release` workflows.

## What was added

- `docker-compose.prod.yml` for immutable image-based production deploys
- `.github/workflows/deploy.yml` for build + push + deploy after successful CI on `main`
- `ansible/` with a minimal bootstrap/deploy playbook and roles

## Deployment flow

1. A push reaches `main`.
2. Existing CI runs and must finish successfully.
3. `CD - Build and Deploy` starts from `workflow_run`.
4. GitHub Actions builds a Docker image and pushes it to GHCR.
5. GitHub Actions runs Ansible against the target server.
6. Ansible copies `docker-compose.prod.yml` and `.env` into the deploy user's workspace, runs a one-shot migration container, optionally runs a one-shot seed container, and then starts the runtime services.
7. Ansible runs a post-deploy smoke-check: it verifies the core containers are running and, when enabled, probes the health API readiness endpoint from inside the bot container.

## Why production uses a separate compose file

`docker-compose.yml` remains the local/dev entrypoint and still builds from source.

`docker-compose.prod.yml` is intentionally image-based:

- the server does not need the git repository checked out;
- the deployment uses an immutable image tag;
- the deploy host only needs Docker, Compose, `.env`, and persistent volumes.
- database migrations run as a separate one-shot service instead of piggybacking on bot startup.

## Required GitHub secrets

Configure these in the `production` environment or repository secrets:

- `DEPLOY_HOST` - server IP or DNS name
- `DEPLOY_USER` - SSH user used by Ansible
- `DEPLOY_SSH_KEY` - private SSH key for the deploy user
- `DEPLOY_KNOWN_HOSTS` - pinned `known_hosts` entry for the server
- `PROD_ENV_FILE` - full multiline production `.env` file contents

Optional secrets:

- `DEPLOY_PORT` - SSH port, defaults to `22`
- `DEPLOY_PATH` - application directory on the server, defaults to `/home/ilya/pybot`
- `GHCR_DEPLOY_USERNAME` - username for pulling private GHCR images on the server
- `GHCR_DEPLOY_TOKEN` - token for pulling private GHCR images on the server
- `RUN_SEED_ON_DEPLOY` - set to `true` only for the initial deploy when you need to run `fill_point_db.py`

## Expected server shape

The regular CD deploy assumes:

- Docker is already installed on the server
- the deploy user can run Docker commands without `sudo`
- the deploy path is writable by the deploy user

An optional bootstrap playbook is still available for Debian/Ubuntu hosts:

- [`ansible/playbooks/bootstrap.yml`](/e:/StudBot/PyBot_ITAcadem/ansible/playbooks/bootstrap.yml#L1)
- it installs `docker.io` and `docker-compose-plugin`
- it is intentionally separate from the normal CD path so routine deploys do not mutate shared server infrastructure

The app is deployed into `/home/ilya/pybot` by default and keeps persistent data in named Docker volumes:

- `pybot_data_prod`
- `pybot_redis_data_prod`

The deploy also persists the currently released image reference as `APP_IMAGE` inside the server-side `.env`, so routine manual commands like `docker compose ps` and `docker compose logs` work without extra exports.

## Notes about ports

`docker-compose.prod.yml` does not publish any host ports.

That means:

- Redis stays internal to the Docker network
- the bot does not reserve any host port
- health API will also stay internal unless you explicitly add a `ports` mapping later

## Safety for Shared Servers

The normal CD flow is intentionally non-root:

- it does not install packages during routine deploys
- it does not change system services during routine deploys
- it only writes inside the configured deploy path and uses Docker commands available to the deploy user

This separation is meant to reduce the risk of affecting unrelated projects hosted on the same server.

## Post-Deploy Smoke Check

The deploy role performs a lightweight smoke-check after `docker compose up -d`:

- verifies that `pybot-bot`, `pybot-taskiq-worker`, `pybot-taskiq-scheduler`, and `pybot-redis` are running;
- waits for Redis health to become `healthy` when a healthcheck exists;
- if `HEALTH_API_ENABLED=true`, calls `GET /ready` from inside the bot container.

This complements CI tests by validating the deployed runtime on the real server instead of rerunning the same test suite.

## Migrations

Production migrations are executed by the dedicated `migrate` service in `docker-compose.prod.yml`.

That service is attached to the `migration` profile, so:

- it is run explicitly by Ansible during deploy;
- it is not started by a plain `docker compose up -d` against the production compose file;
- local development remains unchanged because the regular `docker-compose.yml` still uses the original startup flow.

## Seed

Production seed data is handled by the dedicated `seed` service in `docker-compose.prod.yml`.

- it is disabled by default;
- it runs only when `RUN_SEED_ON_DEPLOY=true` is passed from GitHub Secrets into the deploy workflow;
- it is intended for first deploys or controlled reinitialization, not for every rollout.

## Recommended production `.env` baseline

At minimum, set:

- `BOT_TOKEN`
- `BOT_TOKEN_TEST`
- `BOT_MODE=prod`
- `ROLE_REQUEST_ADMIN_TG_ID`
- `DATABASE_URL=sqlite+aiosqlite:///./data/pybot_itacadem.db`
- `FSM_STORAGE_BACKEND=redis`
- `REDIS_URL=redis://redis:6379/0`
- `AUTO_SEED_DB=false`
- `LOG_LEVEL=INFO`
- `HEALTH_API_ENABLED=false`

Important:

- if you use SQLite in production, keep `DATABASE_URL` under `./data/...`
- paths like `sqlite+aiosqlite:///./pybot_itacadem.db` will place the database outside the mounted volume and break one-shot migration/seed containers

## Next hardening steps

- Add a rollback workflow that redeploys a previous image tag
- Add external monitoring/log shipping
- Add image vulnerability scanning before deploy
