
# Part 3 — Portability and State (CityBite)

## 1. Overview

This section explains how CityBite manages stateful data and ensures portability across development, CI pipelines, and Kubernetes production environments. The goal is to guarantee that the same container behaves consistently in every environment.

---

## 2. Menu Uploads (State Management)

CityBite stores restaurant menu images, which are binary files requiring persistent storage.

We evaluate two approaches:

---

### 2.1 Option A: Kubernetes Persistent Volume (PVC)

**Description:**  
A Kubernetes-managed filesystem volume mounted into pods.

**Advantages:**
- Simple to integrate with Kubernetes workloads
- Low-latency local file access
- Works well for single-cluster deployments

**Disadvantages:**
- Tightly coupled to cluster infrastructure
- Hard to migrate between cloud providers
- Requires manual backup strategy

---

### 2.2 Option B: Object Storage (Recommended)

**Example:** AWS S3 (or equivalent like GCS / Azure Blob Storage)

**Advantages:**
- Highly scalable and durable
- Fully decoupled from Kubernetes
- Built-in redundancy and lifecycle management
- Works across regions and clusters

**Disadvantages:**
- Slightly higher latency than local disk access
- Requires SDK-based integration instead of filesystem writes

---

### 2.3 Final Decision

CityBite uses **object storage as the primary storage solution**.

This is because:
- Menu uploads spike during dinner peak hours
- Storage must scale independently from compute
- Cross-region availability is required

In this design:
- `DATA_DIR` is used only for local development or optional PVC-based setups
- Production uses direct object storage access (e.g. AWS S3 SDK)

---

## 3. Secrets Management

Sensitive data includes:
- Payment API keys
- Database credentials
- Authentication tokens

---

### 3.1 Storage Rules

Secrets must NEVER be stored in:
- Docker images
- Git repositories
- VM filesystem

---

### 3.2 Kubernetes Approach

- Use Kubernetes Secrets for runtime injection
- Optionally integrate with external secret managers (e.g. AWS Secrets Manager)

---

### 3.3 Injection Method

Secrets are injected into pods as environment variables:
- `DATABASE_URL`
- `PAYMENT_API_KEY`

---

## 4. Database Strategy

CityBite uses a **managed PostgreSQL database outside Kubernetes**.

---

### 4.1 Rationale

- Avoids running stateful databases inside the cluster
- Improves reliability and backup support
- Allows independent scaling of compute and storage

---

### 4.2 Connectivity

Pods connect using:

- `DATABASE_URL` injected at runtime

Example:

Example:
postgresql://user:password@db.citybite.internal:5432/orders


---

## 5. Dev vs Production Parity

To ensure portability, CityBite maintains consistent runtime behavior across environments.

### 5.1 Development Environment

Developers use:

- Docker containers locally
- Docker Compose for multi-service setup
- Local volume mounts to simulate storage behavior

### 5.2 Production Environment

- Kubernetes runs identical container images
- Configuration injected via environment variables
- Storage is handled via object storage (S3) or optional PVC

---

## 6. Key Portability Principle

CityBite follows a strict portability rule:

> The same container image must run unchanged across laptop, CI pipeline, and Kubernetes cluster.

This is achieved through:
- Environment-based configuration (`PORT`, `DATABASE_URL`, `DATA_DIR`)
- Externalized state (object storage / volumes)
- Immutable container images

