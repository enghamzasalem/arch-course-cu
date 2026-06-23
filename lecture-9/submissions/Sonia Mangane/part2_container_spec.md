# Task 2.1: Container Spec & Runtime Contract

## 2.1 Image Definition
* **Base Image:** `python:3.11-slim`. 
* **Reasoning:** Minimizes image size for faster pulls during dinner spikes and reduces the security attack surface by removing unnecessary OS utilities.

## 2.2 Dockerfile Sketch (CityBite API)
```dockerfile
FROM python:3.11-slim

# Security: Run as non-root user
RUN useradd -m citybiteuser
WORKDIR /app

# Dependency layer (cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application layer
COPY . .
RUN chown -R citybiteuser:citybiteuser /app

USER citybiteuser

# Runtime Contract
ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]
```

## 2.3 Runtime Contract & Process Model
Process: One main process per container (the API server). Background workers run in a separate Deployment using the same image but different start commands.

Logs: All logs are emitted to stdout/stderr.

Environment Variables:

PORT: Injected by K8s Service (default 8080).

DATABASE_URL: Connection string for RDS Postgres.

DATA_DIR: Path to the mounted upload volume (e.g., /data/uploads).



