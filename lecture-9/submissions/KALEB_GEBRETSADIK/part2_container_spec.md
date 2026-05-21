# Part 2: Containers and Runtime Contract

## Task 2.1: Container Images and Process Model

### 1. Base Image and Build Steps

**Base Image Choice:** `python:3.11-slim`
**Why?** The `slim` image trims out unnecessary OS compilers and libraries included in the massive default image, significantly minimizing vulnerability surface areas and reducing network pull latency. While `alpine` variants are smaller, running Python applications relying on compiled C-extensions (like the `psycopg2` PostgreSQL driver) on Alpine usually necessitates manually compiling heavy packages via `musl`, stripping away all performance benefits. The `slim` variant offers maximum stability with strong security.

**High-Level Build Steps:**
1. Provision the base system and install bare-minimum runtime libraries (e.g., `libpq` for database connection).
2. Establish a dedicated, explicitly non-root user account (e.g., `citybite_runner`) to enforce structural least-privilege logic.
3. Copy the `requirements.txt` dependency manifest and install pip packages. (Doing this before copying the full source code maximizes Docker's layer cache).
4. Copy the actual CityBite application source code (`main.py`, modules) into a scoped `/app` working directory.
5. Apply correct ownership permissions to directory paths for the non-root user.
6. Assert the non-root identity via `USER`.
7. Terminate with the unified execution `CMD` directive pointing to the web server.

---

### 2. Runtime Contract

The container interacts with the surrounding Kubernetes orchestration explicitly through Environment Variables and Standard Streams.

**Required Environment Variables:**
*   `PORT`: The HTTP listener port dynamically injected by the host orchestrator.
*   `DATABASE_URL`: Connection URL addressing the centralized Amazon RDS PostgreSQL repository.
*   `LOG_LEVEL`: Active telemetry threshold (`INFO`, `DEBUG`).
*   `AWS_REGION`: Specifies the host deployment location (`us-east-1`).
*   `S3_BUCKET_NAME`: Unlocks cloud-native menu uploads directly bypassing the hard-disk.

**Listening Port:**
The web application must dynamically bind its listen target strictly to reading the `PORT` env var (e.g., `0.0.0.0:$PORT`) rather than hardcoding. 

**Logging:**
All execution, security, and access logs leave the application exclusively by streaming unbuffered json logs strictly to `stdout` and `stderr`.
*   **Justification:** Forwarding logs to standard output naturally allows standard Kubernetes node agents (such as FluentBit or Promtail) to reliably pick up and ship the logs automatically to central storage (Datadog/CloudWatch) with automatic pod-metadata tagging. Relying on an intra-container log file plus a sidecar container adds completely unnecessary architectural complexity for standard Python HTTP logs.

---

### 3. Single Responsibility Process

**Design Decision:** We will enforce a strict single-process model (One Main Process PID 1 per container).
**Justification:** The container's primary lifecycle execution will solely consist of the Orders API Web Server (e.g. Uvicorn/Gunicorn). Any background dispatch retry logic will be separated entirely into a distinctly deployed **Worker Pod**. Running a process manager (like `supervisord`) to run *both* the web API and background worker in the exact same container masks individual crash errors from Kubernetes and prevents independent scaling (e.g., if we hit a massive traffic spike, scaling the single container spins up unnecessary workers, wasting expensive compute resources).

---

### 4. API Dockerfile Sketch

```dockerfile
# Base off officially maintained slim image
FROM python:3.11-slim

# Enforce secure Python execution streams
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for PostgreSQL clients
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Add unprivileged runtime user
RUN useradd -m citybite_runner

# Leverage caching mechanisms explicitly for dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Inject remaining source logic
COPY . .

# Restrict scope permissions strictly
RUN chown -R citybite_runner:citybite_runner /app
USER citybite_runner

# Execute natively parsing environment injection PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
```
