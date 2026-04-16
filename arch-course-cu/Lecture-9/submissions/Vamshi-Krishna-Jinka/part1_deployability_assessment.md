# Part 1: Deployability Assessment — CityBite

## Overview

CityBite currently runs as a monolith on long-lived VMs with manual deployment practices. This creates inconsistencies, downtime risks, and operational overhead. The goal of moving to **Kubernetes (AWS EKS)** with containerized services is to enable **repeatable, reliable, and low-risk deployments** aligned with modern deployability principles.

---

## Deployability Risks and Mitigations

### 1. Host Drift (Snowflake Servers)

**Problem:**
Each VM is slightly different due to manual configuration and patching. This leads to unpredictable behavior across environments.

**Mitigation:**

* Use **immutable container images** built via CI pipelines
* Pin deployments to **image digests (e.g., `image: citybite/api@sha256:...`)** in Kubernetes
* Ensures identical runtime across dev, staging, and production

---

### 2. Manual SSH-Based Deployments

**Problem:**
Deployments are performed manually via SSH scripts, increasing human error and making rollbacks slow and unreliable.

**Mitigation:**

* Use **Kubernetes Deployments with rolling updates**
* Configure:

  * `maxUnavailable: 0`
  * `maxSurge: 1`
* Enable **automated rollbacks** via failed readiness probes
* Integrate CI/CD (e.g., GitHub Actions) to push images and update manifests

---

### 3. Configuration Drift and Secret Leakage

**Problem:**
Configuration is stored in `.env` files on VMs, with some secrets historically committed to Git.

**Mitigation:**

* Use **Kubernetes ConfigMaps** for non-sensitive config (`LOG_LEVEL`, `PORT`)
* Use **Kubernetes Secrets** or **AWS Secrets Manager** for sensitive values (`DATABASE_URL`)
* Inject configuration via environment variables at runtime (as shown in )

---

### 4. Tight Coupling to Local Disk (Uploads)

**Problem:**
Menu images are stored on VM local disk (`/var/citybite/uploads`), causing data loss on restarts and preventing horizontal scaling.

**Mitigation:**

* Use **persistent volumes (EFS via CSI driver in EKS)** or **S3 object storage**
* Standardize access using `DATA_DIR` environment variable (as shown in )
* Mount volume into containers at a consistent path (e.g., `/var/data`)

---

### 5. Downtime During Deployments

**Problem:**
Restarting the monolith causes minutes of partial downtime, especially during peak dinner traffic.

**Mitigation:**

* Implement **readiness and liveness probes** in Kubernetes
* Use **rolling deployments** to ensure zero-downtime updates
* Add **Horizontal Pod Autoscaler (HPA)** to handle traffic spikes dynamically

---

### 6. Lack of Standardized Logging and Observability

**Problem:**
Logs are written to local files, making aggregation and debugging difficult.

**Mitigation:**

* Emit **structured JSON logs to stdout** (as shown in )
* Use centralized logging (e.g., **CloudWatch Logs** or **Loki**)
* Attach metadata (service name, region, request ID) for traceability

---

## Trade-off: What Becomes Harder

### Increased Complexity in Debugging Distributed Systems

**Challenge:**
Moving from a monolith on a single VM to multiple containerized services introduces complexity in debugging issues across services, pods, and environments.

**Mitigation:**

* Use **centralized logging and tracing** (e.g., OpenTelemetry + Jaeger)
* Enable **kubectl port-forward** and **ephemeral debug containers** for live debugging
* Maintain **local development parity** using Docker Compose or Kind (Kubernetes in Docker)

---

## Summary

By adopting Kubernetes (EKS), CityBite improves deployability through:

* **Immutable, reproducible deployments**
* **Environment-driven configuration**
* **Zero-downtime rollouts**
* **Decoupled storage and compute**
* **Centralized observability**

These changes directly address the current operational pain points while enabling scalable and reliable delivery of features.
