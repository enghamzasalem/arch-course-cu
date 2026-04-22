**part2_container_spec.md**

1.  **Image Strategy & Process Model:** We are moving away from
    \"everything-on-one-server\" to a **modular process model**.

-   **Base Image Selection:** python:3.11-slim-bullseye

```{=html}
<!-- -->
```
-   **The \"Why\":** We avoid the standard python:3.11 because it
    includes build tools and compilers that increase the image size to
    \~900MB and add security vulnerabilities. We avoid alpine because
    Python's C-extensions (like psycopg2 for Postgres) are compiled
    against glibc (Debian/Ubuntu), whereas Alpine uses musl. Using slim
    prevents complex, slow builds and \"segmentation fault\" errors
    during runtime.

```{=html}
<!-- -->
```
-   The Build Pipeline (The \"Layers\"):

1.  **System Dependencies:** Install libpq-dev (essential for
    PostgreSQL) and curl (for health check debugging).

2.  **Deterministic Dependencies:** Copy only requirements.txt first. By
    running pip install before copying the rest of the code, we ensure
    that if you only change a line of code, Docker uses the cached
    \"dependencies\" layer, reducing build time from minutes to seconds.

3.  **Security Hardening:** We use RUN useradd -m cityuser. In the
    baseline VM, scripts often run as root. In K8s, if a container is
    compromised, running as a non-privileged user prevents the attacker
    from modifying the system or escaping to the host node.

-   **Process Architecture:** \* **Container A (The API):** Entrypoint
    is the Gunicorn web server.

```{=html}
<!-- -->
```
-   **Container B (The Worker):** Uses the **same image** but we
    override the CMD in the K8s manifest to run python
    worker_dispatch.py. This ensures the API and Worker always have the
    same library versions, but can be scaled independently (e.g., more
    workers during peak dinner hours).

2.  **The Runtime Contract:** The application must follow the
    Twelve-Factor App methodology for configuration and output.

-   **Port Mapping:** The container exposes PORT=8080. We do not
    hardcode this. The app reads the PORT env var. K8s maps the external
    load balancer to this internal port.

-   **Environment Variables:**

```{=html}
<!-- -->
```
-   **DATABASE_URL:** Stored in a K8s Secret. It contains the host,
    port, user, and password for RDS.

-   **DATA_DIR:** This is a Volume Mount. We tell the app to look for
    uploads at /app/uploads, which K8s connects to a Persistent Volume
    (EFS).

```{=html}
<!-- -->
```
-   **Logging:** The app is configured to log to sys.stdout.

```{=html}
<!-- -->
```
-   **Justification:** On a VM, logs rotate and fill up disks. In K8s,
    we treat logs as an event stream. By writing to stdout, the K8s Log
    Driver collects them. If a Pod crashes, we can still see why by
    running kubectl logs \--previous.

3.  **Detailed Dockerfile (API):**

**\# Stage 1: Build/Production Image**

**FROM python:3.11-slim-bullseye**

**\# 1. Set environment safeguards**

**ENV PYTHONDONTWRITEBYTECODE=1 \\**

**PYTHONUNBUFFERED=1 \\**

**PORT=8080**

**WORKDIR /app**

**\# 2. Install essential system libraries (Postgres + Health Tools)**

**RUN apt-get update && apt-get install -y \\**

**libpq-dev \\**

**gcc \\**

**curl \\**

**&& rm -rf /var/lib/apt/lists/\***

**\# 3. Leverage Docker Cache for Dependencies**

**COPY requirements.txt .**

**RUN pip install \--no-cache-dir -r requirements.txt**

**\# 4. Copy Application Source**

**COPY . .**

**\# 5. Security: Create a non-root user**

**RUN useradd -m cityuser && chown -R cityuser /app**

**USER cityuser**

**\# 6. Expose and Run**

**EXPOSE 8080**

**\# Using \'exec\' form for proper signal handling (SIGTERM)**

**CMD \[\"gunicorn\", \"\--bind\", \"0.0.0.0:8080\", \"\--workers\",
\"4\", \"app:app\"\]**
