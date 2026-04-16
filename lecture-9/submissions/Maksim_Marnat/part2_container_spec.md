# Part 2.1 — Container images and runtime contract

**Scope:** **citybite-order-api** (required), **citybite-dispatch-worker** (optional background retries for dispatch/outbox). Both share the same repo artifact; worker overrides `CMD`.

## Images

| Image | Base | Rationale |
|-------|------|-----------|
| `citybite-order-api` | `python:3.12-slim-bookworm` | Official, small, glibc-compatible; security patches via upstream tags; matches Python examples in lecture. |
| `citybite-dispatch-worker` | Same base | One supply chain; different entrypoint only. |

**Build (high level):** `pip install --no-cache-dir -r requirements.txt` → copy application tree → **`useradd` + `USER appuser`** (non-root) → default `CMD` starts **gunicorn/uvicorn** binding **`0.0.0.0:$PORT`**.

## Runtime contract (env)

| Variable | Required | Purpose |
|----------|----------|---------|
| `PORT` | yes | HTTP listen port (EKS sets via container spec; local default `8080`). |
| `DATABASE_URL` | yes | Postgres URL (RDS); never default to prod in image. |
| `LOG_LEVEL` | no | `INFO` / `DEBUG`. |
| `AWS_REGION` | yes (prod) | e.g. `eu-central-1`. |
| `DATA_DIR` | dev/stage | Writable root for **local** menu uploads (compose volume); prod uses S3 — see Part 3. |
| `MENU_S3_BUCKET` | prod | Bucket name for menu objects (extends reference table; consistent across manifests). |

Payment keys: `PAYMENT_PROVIDER_API_KEY` injected from **Secret**, not shown in Dockerfile.

## Logs

**Stdout only**, one JSON object per line (compatible with `example1`): shipper is **CloudWatch Logs** / Fluent Bit DaemonSet — **no** log files inside the container.

## Process model

**One main process per container:** API container runs only the WSGI server; worker container runs only the worker process. Sidecars (e.g. Envoy) are out of scope unless added later — avoids two “main” apps fighting PID 1.

## Dockerfile sketch — API only

```dockerfile
FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser
EXPOSE 8080
# Shell form so $PORT expands at container start (injected by EKS).
CMD ["/bin/sh", "-c", "exec gunicorn -w 2 -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:${PORT:-8080}"]
```
