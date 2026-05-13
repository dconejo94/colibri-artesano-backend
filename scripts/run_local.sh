#!/bin/bash
set -e

echo "Starting services..."
docker compose up -d --build

echo "Running migrations..."
docker compose exec backend uv run alembic upgrade head

echo "Backend ready:"
echo "http://localhost:8000"

echo "Swagger"
echo "http://localhost:8000/docs"

docker compose logs -f backend