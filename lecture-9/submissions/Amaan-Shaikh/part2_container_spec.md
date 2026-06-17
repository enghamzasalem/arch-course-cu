# Part 2.1 – Container Specification

## Base Image

**Choice:** `python:3.11-slim`

**Why:** Small footprint, good security, official image, matches lecture examples.

## Build Steps (API Image)

1. Set working directory `/app`
2. Install system dependencies (`libpq`, `gcc`)
3. Copy `requirements.txt` and run `pip install`
4. Copy application code
5. Create non-root user `citybite`
6. Set `USER citybite`
7. Set `CMD ["python", "main.py"]`

## Runtime Contract (Env Vars)

| Variable | Required | Purpose |
|----------|----------|---------|
| `PORT` | Yes | HTTP bind port |
| `DATABASE_URL` | Yes | Postgres connection string |
| `LOG_LEVEL` | No | Default INFO |
| `DATA_DIR` | Yes | Uploads directory (PVC) |

## Logging

Logs go to **stdout/stderr** – captured by Kubernetes, sent to Cloud Logging.

## Single Responsibility

One main process per container (the API server). No sidecar in same container.

## Dockerfile Sketch

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --no-create-home citybite
USER citybite

ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]

```
