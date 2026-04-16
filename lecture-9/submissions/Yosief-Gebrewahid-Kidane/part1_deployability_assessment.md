# Part 1 — Deployability Assessment (CityBite)

## 1. overview

CityBite currently runs as a monolithic application deployed on long-lived virtual machines (VMs). While this setup is functional, it creates several operational and deployability challenges, especially under peak traffic conditions such as evening dinner spikes.

This document identifies key deployability issues and proposes improvements enabled by containerization and Kubernetes.

---

## 2. Deployability Risks and Mitigations

### 2.1 Host Drift (Snowflake VMs)

**Problem:**  
Each VM is configured manually via SSH, leading to inconsistencies between environments.

**Impact:**
- Different runtime behavior across machines
- Hard-to-reproduce production bugs
- Unreliable rollback process

**Mitigation:**
- Use immutable Docker images
- Deploy via Kubernetes using image digests (e.g., `sha256`)
- Eliminate manual server configuration

---

### 2.2 Manual Deployment Process

**Problem:**  
Deployments are performed manually using SSH scripts.

**Impact:**
- High risk of human error
- No repeatability or audit trail
- Slow release cycles

**Mitigation:**
- Introduce CI/CD pipeline
- Build Docker images automatically
- Deploy using Kubernetes manifests or Helm

---

### 2.3 Configuration Stored on Disk

**Problem:**  
Environment configuration is stored in `.env` files on each VM, sometimes inconsistently or insecurely.

**Impact:**
- Secrets may leak into version control
- Environment drift across servers

**Mitigation:**
- Use environment variables (`PORT`, `DATABASE_URL`, `LOG_LEVEL`)
- Store secrets in Kubernetes Secrets or external secret managers

---

### 2.4 Local Filesystem Dependency

**Problem:**  
Menu images are stored on VM disk (`/var/citybite/uploads`).

**Impact:**
- Data loss if VM fails
- Cannot scale horizontally
- No shared storage across replicas

**Mitigation:**
- Use object storage (e.g., AWS S3)
- Or Kubernetes Persistent Volumes (PVCs) for limited cases
- Abstract storage using `DATA_DIR` or storage SDK

---

### 2.5 Downtime During Deployments

**Problem:**  
Restarting the monolith causes downtime during deployments.

**Impact:**
- Lost requests during peak hours
- Poor user experience

**Mitigation:**
- Use Kubernetes rolling updates
- Gradually replace old pods with new pods
- Ensure zero downtime via readiness probes

---

### 2.6 Lack of Health Monitoring

**Problem:**  
No standardized health-check system exists.

**Impact:**
- Failed instances may still receive traffic
- Late detection of outages

**Mitigation:**
- Implement liveness probes (restart unhealthy containers)
- Implement readiness probes (control traffic routing)

---

## 3. Trade-off: Increased System Complexity

Moving to Kubernetes introduces additional complexity:

- More components (pods, services, deployments)
- Distributed system debugging challenges
- Steeper operational learning curve

**Mitigation strategies:**
- Centralized logging (stdout aggregation)
- Monitoring tools (Prometheus, Grafana)
- Local development via Docker Compose