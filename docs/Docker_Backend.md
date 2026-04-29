# Docker Backend

The integrated backend runs in Docker and expects Supabase to remain an external service.

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
- The frontend intake form still needs its submit flow wired to the backend API client before patient intake is fully connected.

## Command Reference

Validate Compose configuration:

```bash
docker compose config
docker compose --profile test config
docker compose --profile smoke config
```

Build the backend image:

```bash
docker compose build api
```

Build the backend image directly:

```bash
docker build -t medical-ai-triage-backend ./backend
```

Run the backend API:

```bash
docker compose up --build api
```

Run the backend API in the background:

```bash
docker compose up -d --build api
```

Check backend health:

```bash
curl http://localhost:8000/health
docker compose ps
```

View backend logs:

```bash
docker compose logs -f api
```

Run backend tests in Docker:

```bash
docker compose --profile test run --rm api-test
```

Run live Supabase smoke checks:

```bash
docker compose --profile smoke run --rm api-smoke
```

Stop and remove Docker resources for this Compose project:

```bash
docker compose down
```

Stop and remove containers plus local named volumes for this Compose project:

```bash
docker compose down --volumes
```

Remove the direct-build backend image:

```bash
docker image rm medical-ai-triage-backend
```

## CI Command Sequence

A minimal CI job can run:

```bash
docker compose config
docker compose build api
docker compose --profile test run --rm api-test
docker compose down
```

For a CI job with real Supabase secrets, add:

```bash
docker compose --profile smoke run --rm api-smoke
```
