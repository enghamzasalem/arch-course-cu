# Part 2: Containers and Runtime Contract — CityBite

---

## 2.1 Container Images and Process Model

### API Image

**Base image:** `python:3.12-slim`

Chosen for three reasons. First, the `slim` variant strips the full CPython test suite, documentation, and most optional shared libraries, giving a starting layer of roughly 130 MB versus ~370 MB for the full image — smaller attack surface and faster ECR pull on cold starts. Second, it is an official Docker Library image with a documented, signed provenance chain, which satisfies CityBite's supply-chain audit requirement. Third, Python 3.12 is the current stable release with active security patches; pinning the minor version in the `FROM` line (`python:3.12-slim`) rather than a floating `python:slim` tag ensures reproducible builds across CI runs.

**Build steps (high level):**

1. Set working directory to `/app`.
2. Copy `requirements.txt` only (before copying the rest of the source) so that Docker's layer cache retains the dependency layer on source-only changes.
3. Install Python dependencies with `pip install --no-cache-dir` to avoid storing the pip HTTP cache inside the image layer.
4. Copy the application source code.
5. Create a non-root system user (`citybite`, UID 1001) and `chown` the working directory to it. This is a hard requirement for EKS node groups that enforce `runAsNonRoot: true` in the Pod Security Standard.
6. Switch to that user with `USER citybite`.
7. Set `ENV PORT=8080` as a default that the Kubernetes Deployment can override via its `env` block.
8. Declare `EXPOSE 8080` (documentation only — Kubernetes uses the Service port mapping, not EXPOSE).
9. Set `CMD` to launch Uvicorn with `--host 0.0.0.0` so the socket binds on all interfaces, not just loopback.

---

### Worker Image (optional — dispatch retry worker)

**Base image:** `python:3.12-slim` (same as API, same rationale).

The worker image shares the same `requirements.txt` as the API because the retry logic imports shared domain models. The only difference from the API image is the `CMD`, which runs the worker entry point (`python -m citybite.worker`) instead of Uvicorn. This keeps the two images as a single-build, two-tag output in CI rather than maintaining a separate Dockerfile, which reduces drift between production images.

**Build steps:** identical to the API image steps 1–6 above; step 9 replaces the Uvicorn command with the worker entry point.

---

## Dockerfile Sketch — API Image

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements first to exploit layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY citybite/ ./citybite/

# Non-root user (required by EKS Pod Security Standard)
RUN adduser --system --uid 1001 citybite \
    && chown -R citybite /app
USER citybite

# Default port — overridden by Deployment env block at runtime
ENV PORT=8080
EXPOSE 8080

# Graceful shutdown: Uvicorn handles SIGTERM and drains in-flight requests
CMD ["python", "-m", "uvicorn", "citybite.api:app", \
     "--host", "0.0.0.0", "--port", "8080", \
     "--workers", "1", "--timeout-graceful-shutdown", "30"]
```

**Notes on specific choices:**

`--workers 1` — Uvicorn's multi-worker mode forks additional OS processes inside the container. Since Kubernetes scales horizontally by adding pods (each a single process), forking inside a container bypasses the scheduler's visibility into actual concurrency. One worker per container keeps resource requests honest and lets the HPA reason accurately about CPU.

`--timeout-graceful-shutdown 30` — when Kubernetes sends `SIGTERM` (at the start of pod termination), Uvicorn stops accepting new connections and allows up to 30 seconds for in-flight HTTP requests to complete before the process exits. This pairs with the Deployment's `terminationGracePeriodSeconds: 45` to ensure no requests are dropped during a rolling update.

---

## Runtime Contract

### Environment Variables

| Variable | Required | Example value | Source in K8s |
|---|---|---|---|
| `PORT` | Yes | `8080` | ConfigMap or hardcoded in Deployment `env` |
| `DATABASE_URL` | Yes | `postgresql://user:pass@rds-host:5432/citybite` | Secret (from AWS Secrets Manager via ASCP) |
| `LOG_LEVEL` | Yes | `INFO` | ConfigMap |
| `DATA_DIR` | Yes | `/mnt/uploads` | ConfigMap (must match EFS PVC `mountPath`) |
| `AWS_REGION` | Yes | `eu-central-1` | ConfigMap |
| `WORKER_CONCURRENCY` | No | `4` | ConfigMap (worker image only) |
| `SENTRY_DSN` | No | `https://…@sentry.io/…` | Secret |

All variables are injected by the Kubernetes platform at pod startup via `envFrom` (ConfigMap) and `env.valueFrom.secretKeyRef` (Secret). No variable is baked into the image at build time. This is what makes the same image portable across local Docker Compose, the CI integration test environment, and production EKS — the binary is identical; only the injected values change.

### Listening Port

The API process binds to `0.0.0.0:$PORT`. The value of `PORT` defaults to `8080` in the Dockerfile and is documented in the Deployment manifest. The Kubernetes Service targets `containerPort: 8080` by name (`http`). If the port ever needs to change, it is changed in the ConfigMap only; no image rebuild is required.

### Log Strategy: stdout, no sidecar

All application logs are written to **stdout** (INFO and above in production, DEBUG available via `LOG_LEVEL`). No log file is written to disk. This is the correct approach for a containerised workload for two reasons.

First, Kubernetes captures everything a process writes to stdout/stderr and makes it available via `kubectl logs` and the cluster's log aggregation pipeline (Fluent Bit on each node ships to CloudWatch Logs). Writing to a file instead would require either a sidecar container to tail and forward the file, or a hostPath volume — both add complexity without benefit.

Second, stdout logging means the container has no write dependency on the filesystem for its core operation. `DATA_DIR` is the only writable path the container needs, and that is exclusively for menu image uploads.

A sidecar would be justified if CityBite needed to ship logs to a destination that Fluent Bit cannot reach (e.g. a legacy on-premises SIEM that requires a proprietary agent). That is not the case here.

---

## Single Responsibility

Each container runs exactly one main process:

- **citybite-api pod:** one Uvicorn process serving HTTP on `$PORT`. No background threads perform I/O beyond the database connection pool.
- **citybite-worker pod:** one Python worker process consuming the job queue. No HTTP server runs inside this container.

No exception to single-process-per-container is needed. The background retry jobs that previously ran inside the monolith process are extracted into the separate worker Deployment. This separation means the API and worker can be scaled, deployed, and restarted independently. A surge in restaurant order retries does not affect API pod availability, and restarting a crashed worker pod does not interrupt customer-facing HTTP traffic.
