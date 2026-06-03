# Colibrí Artesano Backend API

This is the backend API for **Colibrí Artesano**, a multi-tenant e-commerce platform designed for artisans. The application provides robust endpoints for user management, multi-store vendor support, product catalog management (including variants and images), and transactional order processing. 

Built with modern Python, it follows a clean, layered architecture ensuring strong ACID compliance and referential integrity.

## Technology Stack

* **Framework:** FastAPI (Python 3.12+)
* **Database:** PostgreSQL 18
* **ORM:** SQLAlchemy 2.0 (Async)
* **Migrations:** Alembic
* **Package Management:** [uv](https://docs.astral.sh/uv/)
* **Validation:** Pydantic

## Architecture

The project strictly follows a 4-Layer Architecture:
1. **API/Routers:** Handles HTTP requests and responses.
2. **Services:** Core business logic and validation.
3. **Repositories:** Abstract data access contracts.
4. **Infrastructure:** Concrete SQLAlchemy implementations.

---

## Getting Started

### Prerequisites

* Docker & Docker Compose
* Python 3.12+ (if running without Docker)
* [uv](https://docs.astral.sh/uv/)

### 1. Environment Setup

Copy the example environment file:
```bash
cp .env.example .env
```

### 2. Running the Application (Quickstart)

The easiest way to run the project is using the included `run_local.sh` script, which will orchestrate Docker Compose to spin up both the FastAPI application and the PostgreSQL database, run Alembic migrations, and seed the initial data.

> **Note for Windows Users:** The `run_local.sh` script requires a bash environment. You will need to run it from **Git Bash** or **WSL**. Alternatively, you can run the Docker commands inside the script manually in PowerShell.

```bash
# Make the script executable (macOS/Linux/Git Bash)
chmod +x scripts/run_local.sh

# Run the services, migrations, and seed data
./scripts/run_local.sh
```

**Available Endpoints:**
* **API Base:** http://localhost:8000/api/v1
* **Swagger/OpenAPI UI:** http://localhost:8000/docs
* **Health Check:** http://localhost:8000/health

**Stopping the services:**
```bash
# Stop and remove containers
docker compose down

# Stop, remove containers, AND wipe the database volume
docker compose down -v
```

### 3. Database Management & Migrations (Reference)

Migrations are handled by Alembic. When running inside Docker, execute these commands against the `backend` container:

**Create a new migration:**
```bash
docker compose exec backend uv run alembic revision --autogenerate -m "describe_your_changes_here"
```

**Apply migrations to the database manually:**
```bash
docker compose exec backend uv run alembic upgrade head
```

**Run database seed manually:**
```bash
docker compose exec -T db psql -U "postgres" -d "colibri" < scripts/seed.sql
```

### 4. Running Tests

The test suite runs against an isolated, in-memory SQLite database (`test.db`) enforcing foreign key constraints.

```bash
# Ensure dependencies are synced
uv sync

# Run tests with coverage
uv run pytest -v --cov=src --cov-report=term-missing
```

### 5. Code Quality (Linting & Formatting)

We use `ruff` for fast linting and formatting.

```bash
# Check for linting errors
uv run ruff check .

# Format code automatically
uv run ruff format .
```
