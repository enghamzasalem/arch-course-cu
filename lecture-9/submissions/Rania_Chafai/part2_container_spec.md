# Part 2 — Container Specification for CityBite

## 1. Overview

CityBite is containerized and deployed on Kubernetes using AWS EKS. Each service runs as an immutable container image stored in Amazon ECR. The system follows a stateless design, while persistent data is stored externally in Amazon RDS (PostgreSQL).

For this deployment design, CityBite is composed of the following services:

| Service  | Image Base       | Port | Stateful |
|----------|------------------|------|----------|
| Frontend | nginx:alpine     | 80   | No       |
| API      | node:18-alpine   | 3000 | No       |
| Redis    | redis:7-alpine   | 6379 | Cache only |
| Worker   | node:18-alpine   | None | No       |

---

## 2. Container Image Strategy

All services are packaged as immutable container images.

- Registry: Amazon ECR
- Images are versioned and tagged (e.g., citybite/api:v1.0.0)
- Images are built automatically via CI/CD

This ensures reproducibility, consistency, and easy rollback.

---

## 3. Application Runtime

Each container includes:

- application code
- runtime environment (Node.js / Nginx / Redis)
- required dependencies

Containers do not depend on the host system, which ensures portability across development, CI, and production environments.

---

## 4. Configuration Management

Configuration is externalized using Kubernetes resources.

### ConfigMap (non-sensitive data)

Used for:
- API endpoint URLs
- Redis host and port
- environment variables

### Secret (sensitive data)

Used for:
- database credentials
- API keys
- authentication tokens

Configuration is injected into containers at runtime via environment variables.

---

## 5. Networking and Ports

| Service  | Port | Exposure |
|----------|------|----------|
| Frontend | 80   | Public via Ingress |
| API      | 3000 | Internal (ClusterIP) |
| Redis    | 6379 | Internal only |
| Worker   | None | Internal only |

Kubernetes Services handle traffic routing and load balancing across pods.

---

## 6. Dependencies

The application depends on:

- Amazon RDS (PostgreSQL) for persistent data
- Redis for caching or background processing

These dependencies are accessed using environment variables and internal service endpoints.

---

## 7. Stateless Design

Application containers are stateless:

- no local data storage
- no session persistence inside containers
- all persistent data is stored externally (RDS)

Benefits:

- horizontal scaling
- easier recovery
- improved reliability

Redis is used only as a cache and does not store critical business data.

---

## 8. Logging and Observability

All containers write logs to stdout and stderr.

Kubernetes collects logs automatically, and in AWS environments, logs can be forwarded to CloudWatch for centralized monitoring and debugging.

---

## 9. Summary

The container specification ensures:

- consistent runtime environments
- portability across development, CI, and production
- scalable and stateless application design
- separation between application logic and persistent data
- support for automated deployment and rollback