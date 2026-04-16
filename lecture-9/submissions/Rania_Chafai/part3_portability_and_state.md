# Part 3 — Portability and State Management for CityBite

## 1. Overview

Portability and state management are key aspects of deploying CityBite on Kubernetes. The goal is to ensure that the application runs consistently across development, CI, and production environments while managing persistent data safely.

The architecture separates stateless application components from stateful services to improve scalability, reliability, and portability.

---

## 2. Portability Strategy

Portability means that the application can run in different environments without modification.

CityBite achieves portability through:

* containerization using Docker
* Kubernetes as a unified runtime platform
* externalized configuration (ConfigMaps and Secrets)
* consistent deployment via CI/CD

These elements ensure that the same container image can be used across all environments.

---

## 3. Portability Across Environments

### Development

* Developers run containers locally using Docker
* Configuration is provided via `.env` files

### CI (Continuous Integration)

* CI/CD builds and tests container images
* Images are stored in Amazon ECR
* Automated tests ensure consistency

### Production

* Kubernetes (AWS EKS) runs the same container images
* Configuration is injected via ConfigMaps and Secrets
* Scaling and deployment are handled automatically

This ensures consistency across environments.

---

## 4. Runtime Consistency

Containers guarantee:

* the same runtime (Node.js, Nginx, Redis) in all environments
* all dependencies are packaged inside the image
* reduced environment-related issues

This eliminates “works on my machine” problems.

---

## 5. Configuration Portability

Configuration is not stored inside container images.

Instead:

* ConfigMap is used for non-sensitive data
* Secret is used for sensitive data

This allows the same container image to be reused with different configurations.

---

## 6. State Management

### Stateless Components

Stateless services include:

* Frontend
* API
* Worker

These components:

* do not store data locally
* can be restarted without data loss
* can be scaled horizontally

---

### Stateful Components

Stateful services include:

* Amazon RDS (PostgreSQL) for persistent data
* Redis for caching

Persistent data is stored outside containers to ensure durability.

---

## 7. Data Persistence Strategy

* Business data is stored in Amazon RDS
* Containers do not rely on local storage
* Data survives pod restarts and failures

This ensures reliability and data integrity.

---

## 8. Scaling Implications

Because application components are stateless:

* Kubernetes can scale pods horizontally
* new instances can be created quickly
* failed pods are automatically replaced

Stateful components require separate scaling strategies.

---

## 9. Portability Benefits

This architecture provides:

* consistent behavior across environments
* easier deployment and maintenance
* reduced configuration errors
* improved scalability and reliability

---

## 10. Summary

CityBite achieves portability through containerization, Kubernetes, and externalized configuration.

State management is handled by separating stateless application components from stateful services such as databases.

This design enables:

* scalable deployments
* reliable system behavior
* environment consistency
* easier system evolution
