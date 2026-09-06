#!/bin/sh
set -e

echo "Applying database migrations..."
# Run alembic migrations
uv run alembic upgrade head

echo "Starting FastAPI server..."
# Start the server with uvicorn
exec uv run uvicorn src.app.main:app --host 0.0.0.0 --port 3009 --reload
