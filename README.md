# Employee Awards Backend

This is a FastAPI backend service for managing employee awards, with:

- PostgreSQL as database
- Redis for task queue
- Celery for background processing
- Prometheus for metrics

## Run Locally

```bash
docker compose up --build

## Recommended sequence for your case

# 1. Stop any running containers
docker compose down

# 2. Rebuild Docker image from scratch (no GPU bloat)
docker compose build --no-cache

# 3. Start containers
docker compose up



### Test the API
Example `curl` commands for your endpoints:


Health check:

```bash
curl http://localhost:8000/healthz
