## Quick Start — Backend

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — Python package manager

### 1. Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install dependencies
```bash
cd backend
uv sync
```

### 3. Set up environment
```bash
cp .env.example .env
```

### 4. Run the app
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0
```

### 5. Verify
- API: http://localhost:8000
- Docs: http://localhost:8000/docs