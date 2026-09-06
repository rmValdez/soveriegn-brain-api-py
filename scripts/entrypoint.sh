#!/bin/sh
set -e

export PYTHONPATH="/app/src:$PYTHONPATH"

echo "Applying database migrations..."
# Run alembic migrations
uv run alembic upgrade head

echo "Starting FastAPI server..."
# Start the server with uvicorn
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 3009 --reload --reload-dir /app/src
