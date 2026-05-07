#!/usr/bin/env sh
set -eu

# Propagate SIGTERM and SIGINT received while alembic or the seed script run.
# Without this, a plain `sh` script ignores SIGTERM during child-process
# execution, which makes Docker hang until the default stop timeout expires.
_on_term() { exit 143; }
_on_int()  { exit 130; }
trap _on_term TERM
trap _on_int  INT

echo "Applying database migrations..."
alembic upgrade head

if [ "${AUTO_SEED_DB:-false}" = "true" ]; then
  echo "Seeding database..."
  pybot-seed
fi

exec python run.py
