#!/usr/bin/env sh
set -eu

echo "Applying database migrations..."
alembic upgrade head

if [ "${AUTO_SEED_DB:-false}" = "true" ]; then
  echo "Seeding database..."
  python fill_point_db.py
fi

exec python run.py
