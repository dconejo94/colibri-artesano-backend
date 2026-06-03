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

### 2. Running with Docker (Recommended)

The easiest way to run the project is using Docker Compose, which spins up both the FastAPI application and the PostgreSQL database.

```bash
# Build and start the services in the background
docker compose up -d --build
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

### 3. Database Management & Migrations

Migrations are handled by Alembic. When running inside Docker, execute these commands against the `backend` container:

**Create a new migration:**
```bash
docker compose exec backend uv run alembic revision --autogenerate -m "describe_your_changes_here"
```

**Apply migrations to the database:**
```bash
docker compose exec backend uv run alembic upgrade head
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
