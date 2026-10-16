# DukaanAI starter

A polished, dependency-free shop dashboard for a small business owner. It is a vanilla Node.js app with static assets and a client-side add-product form.

## Requirements

Node.js 20+ (the pinned runtime is in `.nvmrc`). No dependency installation is needed.

## Setup and run

```bash
cp .env.example .env
npm start
```

Open <http://localhost:3000>. Set `PORT` in `.env` (or the environment) to use another port.

## Test

The test is fully offline and uses only Node's built-in HTTP/fetch/assert APIs:

```bash
npm test
```

It starts the server, requests the main page and JavaScript, and verifies the key dashboard and add-product UI strings.

## Deploy with Docker

```bash
docker build -t dukaanai .
docker run --rm -p 3000:3000 dukaanai
```

Then open <http://localhost:3000>.
