# Docker Backend

This branch runs the FastAPI backend in Docker and expects Supabase to remain an external service.

## Frontend Connection

When running the frontend with Vite on the host machine, point it at the Dockerized backend:

```env
VITE_API_URL=http://localhost:8000
```

Put this in the frontend environment file used by the active frontend branch, for example `frontend/.env.local`.

The backend container must allow the frontend dev server origin through CORS. The root `.env` used by Docker Compose should include:

```env
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

Use `http://localhost:5173` for the default Vite dev server. Keep `http://localhost:3000` only if a frontend branch or tool runs there.

## Start Backend For Frontend Development

Copy the root env template and fill in real secrets locally:

```bash
cp .env.example .env
```

Start the backend:

```bash
docker compose up --build api
```

Verify the backend is reachable from the host:

```bash
curl http://localhost:8000/health
```

Expected response shape:

```json
{"status":"ok","supabase_configured":true,"auth_enabled":true}
```

`supabase_configured` is `false` when `SUPABASE_URL` or `SUPABASE_SERVICE_KEY` is missing.

## Local Auth Bypass

For local smoke testing only, use the dev override:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build api
```

This sets:

```env
AUTH_ENABLED=false
```

Do not use the dev override for shared environments.

## Current Frontend Integration Notes

- The frontend API base URL should come from `VITE_API_URL`.
- The Docker backend is exposed at `http://localhost:8000`.
- CORS must include the frontend origin before browser requests will succeed.
- Queue endpoints require auth unless `AUTH_ENABLED=false` is used for local development.
- The current frontend intake branch still needs its form submit flow wired to the backend API client before patient intake is fully connected.

## Useful Checks

Run the Docker test workflow:

```bash
docker compose --profile test run --rm api-test
```

Run a non-strict smoke test that verifies Docker wiring without real Supabase credentials:

```bash
docker compose --profile smoke run --rm -e SMOKE_REQUIRE_SUPABASE=false api-smoke
```

Run a strict smoke test after `.env` contains real Supabase values:

```bash
docker compose --profile smoke run --rm api-smoke
```
