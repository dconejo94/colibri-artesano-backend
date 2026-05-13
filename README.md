## Quick Start — Backend

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — Python package manager

### 1. Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Run locally

```bash
cp .env.example .env
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

API:
http://localhost:8000

Swagger:
http://localhost:8000/docs

Health:
http://localhost:8000/health

---

## Stop services

```bash
docker compose down
```

---

## Reset database

```bash
docker compose down -v
```

---

## Create migration

```bash
docker compose exec backend uv run alembic revision --autogenerate -m "message"
```

---

## Apply migrations

```bash
docker compose exec backend uv run alembic upgrade head
```

Hot reload is enabled automatically.

