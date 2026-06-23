## Part 2: Containers and Runtime Contract - CityBite

### 2.1 Container Images and Process Model

**Overview**
CityBite is decomposed into two containerized workloads:
* **Order API (required)**: Handles HTTP requests from mobile apps and partners.
* **Background Worker (optional)**: Processes asynchronous jobs such as dispatch retries and notifications.

Each workload runs in its own container and is deployed as a separate Kubernetes Deployment.

**1. Container Images**

**1.1 Order API Image**
* **Base Image Choice**: `python:3.11-slim`.
* **Rationale**: 
    * Minimal footprint leads to faster pull times and reduced attack surface.
    * Official, well-maintained image with security updates.
    * Compatible with typical Python web frameworks like FastAPI or Flask.

**Build Steps (High-Level)**
1. Set working directory (`/app`).
2. Install system dependencies (only if required).
3. Copy `requirements.txt`.
4. Install Python dependencies via pip.
5. Copy application source code.
6. Create and switch to a non-root user.
7. Set environment defaults (e.g., `PYTHONUNBUFFERED=1`).
8. Define container entrypoint (start API server).

**1.2 Background Worker Image**
The worker image is built from the same base image and codebase as the API, but runs a different command.
* **Rationale**: Ensures consistency across services and simplifies the CI pipeline by using a single build for multiple runtime roles.

**2. Runtime Contract**

The runtime contract defines how the container behaves when executed inside Kubernetes.

**2.1 Environment Variables**

| Variable | Purpose |
| :--- | :--- |
| `PORT` | Port on which the API listens (injected by platform) |
| `DATABASE_URL` | Connection string for Amazon RDS PostgreSQL |
| `LOG_LEVEL` | Logging verbosity (e.g. INFO, DEBUG) |
| `AWS_REGION` | AWS region for service integrations |
| `DATA_DIR` | Logical path for uploads (mapped to S3 or volume) |

**Notes**: 
* Sensitive values are injected via external secrets, not baked into the image.
* Signal Handling: The application is configured to handle `SIGTERM` for graceful shutdowns, allowing the API to finish current requests.

**2.2 Networking and Logging**
* **Networking**: The API container listens on `0.0.0.0:${PORT}`.
* **Logging**: All logs are written to `stdout/stderr` in structured JSON format. This avoids file-based logs and allows for centralized observability via Amazon CloudWatch.

**2.3 Process Model**
Each container follows the single responsibility principle:
* **API container**: Runs only the HTTP server (e.g., uvicorn).
* **Worker container**: Runs only the background job processing loop.
* **Justification**: Allows for independent scaling and safer deployments.

**3. Dockerfile Sketch (Order API)**

```dockerfile
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr for faster logging
ENV PYTHONUNBUFFERED=1
# Set logical path for uploads
ENV DATA_DIR=/app/uploads

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd -m appuser
COPY . .
RUN mkdir -p $DATA_DIR && chown -R appuser:appuser /app

USER appuser

# Expose port for documentation
EXPOSE 8080

# Start API server using shell form to allow variable expansion
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

---

### 2.2 Health, Rollout, and Failure

**1. Health Probes**
* **Liveness Probe**: Checks if the process is still running. Path: `/health/liveness`. Threshold: 3 failures.
* **Readiness Probe**: Checks if the app can handle traffic (e.g., DB connection is alive). Path: `/health/readiness`. Initial delay: 10s.

**2. Rolling Update Strategy**
When moving from `v1.4.0` to `v1.5.0`, Kubernetes performs a **Rolling Update**. It spins up a new pod with the new image; once the **Readiness Probe** passes, it terminates an old pod. This ensures zero downtime. If the new pod fails readiness, the rollout halts, leaving the old version running.

**3. Rollback Mechanism**
If a bad deploy is detected via error rate spikes in CloudWatch, a rollback is triggered using `kubectl rollout undo deployment/citybite-api`. This immediately reverts the cluster to the previous stable ReplicaSet.