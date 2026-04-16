# Part 2 — Container Images and Runtime Contract (CityBite)

## 1. Overview

This section defines how the CityBite Order API and an optional background worker are packaged as containers. The goal is to ensure portability, consistency, and scalability across development, CI, and Kubernetes environments.

---

## 2. Container Images

### 2.1 Order API Container

**Base Image:**
- `python:3.11-slim`

**Why this image:**
- Lightweight and production-ready
- Official Python base with security updates
- Smaller attack surface compared to full images

---

**Build steps (high level):**

1. Set working directory (`/app`)
2. Copy dependency file (`requirements.txt`)
3. Install dependencies using `pip`
4. Copy application source code
5. Create non-root user for security
6. Define entrypoint to start API server

---

### 2.2 Background Worker (Optional)

The worker handles asynchronous tasks such as:
- Order retry logic
- Dispatch coordination
- Background processing jobs

**Design decision:**
- Runs as a separate container
- Shares same base image and dependencies as API

**Why this matters:**
- Independent scaling (API vs background load)
- Fault isolation (worker failure does not affect API)
- Clear separation of concerns

---

## 3. Runtime Contract

The container follows a strict runtime contract defined by environment variables and platform expectations.

---

### 3.1 Environment Variables

| Variable | Purpose |
|----------|--------|
| `PORT` | HTTP port for the API |
| `DATABASE_URL` | PostgreSQL connection string |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) |
| `AWS_REGION` | Deployment region |
| `DATA_DIR` | Storage location for uploads (dev/PVC mode) |

**Key principle:**  
All configuration is injected at runtime. The container image contains no environment-specific values.

---

### 3.2 Network Contract

- The API binds to `PORT`
- Default fallback: `8080`

**Why this is important:**
- Kubernetes assigns ports dynamically
- Prevents hardcoded port conflicts
- Ensures portability across environments

---

### 3.3 Logging Contract

- All logs are written to `stdout` and `stderr`

**Reason:**
- Kubernetes automatically collects container logs
- Enables centralized logging systems (e.g., CloudWatch, Loki)
- Avoids dependency on file-based logs inside containers

---

### 3.4 Process Model

Each container runs a single main process:

- **API container:** handles HTTP requests
- **Worker container:** processes background jobs

**Why this design:**
- Simplifies scaling and monitoring
- Aligns with container best practices (one process per container)
- Improves fault isolation

---

## 4. Dockerfile (Order API)

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser
USER appuser

EXPOSE 8080

# Application reads PORT from environment at runtime
CMD ["python", "app.py"]