# DukaanAI

DukaanAI is a reproducible starter for a small-business AI commerce assistant.
This scaffold contains a FastAPI backend, a SQLAlchemy persistence foundation,
an extractor interface with a deterministic mock, and a Vite React TypeScript
placeholder that reports backend health.

## Requirements

- Python 3.12.8 (`.python-version`)
- Node.js 22.14.0 (`.nvmrc`)
- Docker and Docker Compose (recommended)

## Local setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
npm --prefix frontend ci
```

## Run locally

In one terminal:

```bash
uvicorn backend.main:app --reload --port 8000
```

In another:

```bash
npm --prefix frontend run dev
```

Open http://localhost:5173. The page calls `/health`; Vite proxies that request
to the backend at `http://localhost:8000`.

## Test

```bash
make test
```

This runs the backend pytest and a production TypeScript/Vite build. Tests are
offline after dependencies have been installed.

## Docker Compose

```bash
docker compose up --build
```

Open http://localhost:5173 and the API health endpoint at
http://localhost:8000/health. Stop the stack with `Ctrl+C`.
