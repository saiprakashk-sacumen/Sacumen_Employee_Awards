# Employee Awards Backend

This is a FastAPI backend service for managing employee awards, with:

- PostgreSQL as database
- Redis for task queue
- Celery for background processing
- Prometheus for metrics

## Run Locally

```bash
docker-compose up --build


### Test the API
Example `curl` commands for your endpoints:


Health check:

```bash
curl http://localhost:8000/healthz