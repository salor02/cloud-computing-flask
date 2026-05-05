#!/bin/bash
set -e

# this is a redundancy in case of launch by docker compose
echo "Waiting for database..."
wait-for-it.sh "$POSTGRES_HOST:$POSTGRES_PORT" --timeout=60

if [[ ! -d "migrations" ]]; then
    echo "migrations folder does not exist, db needs to be initialized"
else
    echo "Applying database migrations..."
    flask db upgrade
fi

echo "Starting Gunicorn..."
exec "$@"
