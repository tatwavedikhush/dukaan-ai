# DukaanAI

DukaanAI is a small-business commerce assistant that turns product photos and
plain-language descriptions into an editable catalogue, publishes a public
shop page, and lets customers start orders on WhatsApp. It runs locally with a
deterministic extractor by default, so a judge does not need an API key.

## Features

- Create shops with stable, readable slugs.
- Upload up to five product images and describe products in text.
- Extract draft products with the offline mock extractor or optional Gemini.
- Review, edit, publish, and preview a catalogue.
- Browse category filters and order products through WhatsApp.
- Idempotent seven-product `demo-boutique` seeded on startup.
- SQLite schema recovery for the known `image_url` upgrade.

## Demo in 60 seconds

```bash
docker compose up --build
```

Open <http://localhost:5173>, click **View demo shop**, and browse
`/shop/demo-boutique`. To try the creation flow, create a shop, open its
manage page, click **Try it with sample photos**, click **Continue to review**,
review the three sample products, and publish. The demo uses locally generated images and
`MOCK_AI=true`; no key or network-based AI service is required.

![DukaanAI home page](docs/home-screenshot.svg)

![DukaanAI public catalogue](docs/catalogue-screenshot.svg)

## Architecture

```text
React/Vite browser ── JSON + multipart ──> FastAPI API
                                             │
                                             ├─ SQLAlchemy + SQLite
                                             ├─ local uploads
                                             └─ mock extractor / Gemini adapter
```

The frontend runs in its own container and uses Vite's `/api` proxy for local
development. The backend creates tables, repairs the supported SQLite schema
change, creates `uploads/`, and seeds the demo shop during startup.

## Tech stack

- Python 3.12.8, FastAPI, SQLAlchemy, SQLite, pytest
- Node.js 22.14.0, React, TypeScript, Vite, Vitest, React Testing Library
- Docker Compose

## Requirements and local setup

Use Python 3.12.8 from `.python-version` and Node.js 22.14.0 from `.nvmrc`.
Docker and Docker Compose are recommended. For a host-based setup:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
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

Open <http://localhost:5173>. The API health endpoint is
<http://localhost:8000/health>. For the reproducible container run, use:

```bash
docker compose up --build
```

Reset all container data and verify a clean seed with:

```bash
docker compose down -v
```

## Tests

After installing dependencies, the single supported test command is:

```bash
make test
```

It delegates to `scripts/test.sh`, which runs backend pytest, frontend Vitest,
and the frontend TypeScript/Vite production build. The checks are offline
after dependencies are installed.

## Environment variables

Copy `.env.example` to `.env` only when local overrides are needed:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./data/dukaanai.db` in Compose | SQLAlchemy database URL |
| `MOCK_AI` | `true` in Compose | Use the deterministic local extractor |
| `GEMINI_API_KEY` | empty | Optional key when `MOCK_AI=false` |

No key is needed for the default demo. Gemini failures return a clear API
error; they do not crash the server.

## API overview

- `POST /api/shops` creates a shop.
- `POST /api/shops/{slug}/extract` returns unsaved product drafts.
- `POST /api/shops/{slug}/products` publishes reviewed products.
- `GET /api/shops/{slug}` returns a shop and its catalogue.
- `PUT` and `DELETE /api/shops/{slug}/products/{id}` edit catalogue items.

## Known limitations

- There is no authentication, payments, analytics, or multilingual support.
- SQLite and local uploads are intended for demos and small deployments.
- Gemini is an optional adapter and requires the user's own API key.
- WhatsApp ordering opens a prefilled external message; it does not process
  payments or confirm orders.

## What I would build next

I would add shop-owner authentication and permissions, durable image storage,
order capture/status tracking, and deployment observability before using this
for production merchants.

## License

MIT; see [LICENSE](LICENSE).
