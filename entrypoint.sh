#!/bin/bash
set -e

if [[ ! -d "migrations" ]]; then
    echo "migrations folder does not exists, db need to be initialized"
else
    echo "Applying database migrations..."
    flask db upgrade
fi

echo "Starting Gunicorn..."
exec "$@"