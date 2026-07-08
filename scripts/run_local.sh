#!/bin/bash
set -e

echo "Starting services..."
docker compose up -d --build

echo "Running migrations..."
docker compose exec backend uv run alembic upgrade head

echo "Seeding data..."
# Piping seed.sql through a shell redirect (`psql < scripts/seed.sql`) corrupts
# accented characters when this script runs under Git Bash on Windows (the
# UTF-8 bytes get mangled in transit). Copying the file into the container and
# running it with `-f` avoids the host shell entirely, so the bytes reach
# psql unmodified regardless of host OS/shell.
docker cp scripts/seed.sql colibri-postgres:/tmp/seed.sql
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /tmp/seed.sql'

echo "Seeding product images (Azurite blob storage)..."
# scripts/ isn't mounted into the backend container, so copy the script in
# first. Requires AZURE_STORAGE_* to be set in .env (see .env.example) —
# skips itself if storage isn't configured.
docker exec colibri-backend mkdir -p /app/scripts
docker cp scripts/seed_images.py colibri-backend:/app/scripts/seed_images.py
docker exec colibri-backend uv run python scripts/seed_images.py

echo "Backend ready:"
echo "http://localhost:8000"

echo "Swagger"
echo "http://localhost:8000/docs"

docker compose logs -f backend