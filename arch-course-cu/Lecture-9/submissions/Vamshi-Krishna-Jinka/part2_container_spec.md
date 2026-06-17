# Part 2: Containers and Runtime Contract — CityBite

## Overview

In the new architecture, CityBite will run its services as **containers on AWS EKS**.
We define how the **Order API (required)** and **background worker (optional)** run inside containers.
The goal is to make the system **portable, simple, and easy to deploy**.

---

## 1. Container Images

### API Image (Order API)

**Base Image Choice:**

* `python:3.11-slim`
* Reason:

  * Small size → faster download and startup
  * Official and well-supported
  * Enough tools to run Python apps

**Build Steps (High Level):**

1. Set working directory
2. Copy `requirements.txt`
3. Install dependencies using pip
4. Copy application code
5. Create a non-root user (for security)
6. Set environment variables if needed
7. Define the command to start the API

---

### Worker Image (Optional)

**Purpose:**

* Handles background jobs (e.g., dispatch retries)

**Base Image:**

* Same as API (`python:3.11-slim`) → keeps consistency

**Build Steps:**

* Same as API, but runs a different command (worker process instead of web server)

---

## 2. Runtime Contract

The container should not depend on fixed values.
All important configuration comes from **environment variables**.

### Required Environment Variables

| Variable       | Purpose                                             |
| -------------- | --------------------------------------------------- |
| `PORT`         | Port where API listens (set by Kubernetes)          |
| `DATABASE_URL` | Database connection string (Postgres in production) |
| `LOG_LEVEL`    | Logging level (INFO, DEBUG)                         |
| `AWS_REGION`   | AWS region (e.g., eu-central-1)                     |
| `DATA_DIR`     | Path for storing uploaded menu images               |

 This follows the same idea as in  and 
→ configuration is external, not hardcoded.

---

### Listening Port

* The API must listen on the port from `PORT`
* Example: `PORT=8080`
* This makes the container work in any environment (local, Docker, Kubernetes)

---

### Logging Strategy

* Logs are written to **stdout (console)**
* Reason:

  * Kubernetes automatically collects stdout logs
  * No need to manage log files inside containers
  * Easy integration with tools like CloudWatch or Loki

---

## 3. Single Responsibility Principle

* Each container runs **one main process**

### API Container

* Runs only the **web server (Order API)**

### Worker Container

* Runs only the **background worker**

**Why?**

* Easier to scale API and worker separately
* Better fault isolation (if worker fails, API still runs)
* Matches Kubernetes design (one process per container)

---

## 4. Dockerfile (API Image — Sketch)

```dockerfile
# Use small official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser
USER appuser

# Expose port (default)
EXPOSE 8080

# Set environment variables (optional defaults)
ENV PORT=8080
ENV LOG_LEVEL=INFO

# Start the API
CMD ["python", "app.py"]
```

---

## Summary

* We use **lightweight Python images** for fast deployment
* Configuration is passed through **environment variables**
* Logs go to **stdout** for easy monitoring
* Each container runs **one main process**
* This design improves **deployability, portability, and scalability**
