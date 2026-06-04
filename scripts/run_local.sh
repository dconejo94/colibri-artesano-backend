#!/bin/bash
set -e

echo "Starting services..."
docker compose up -d --build

echo "Running migrations..."
docker compose exec backend uv run alembic upgrade head

echo "Seeding data..."
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < scripts/seed.sql

echo "Backend ready:"
echo "http://localhost:8000"

echo "Swagger"
echo "http://localhost:8000/docs"

docker compose logs -f backend