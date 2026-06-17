# CityBite Kubernetes Migration — Assignment README

## Overview

This project explains how **CityBite**, a food delivery system, moves from a **VM-based monolith** to a **container-based architecture using Kubernetes (AWS EKS)**.

The goal is to improve:

* Deployability
* Portability
* Reliability
* Scalability

We applied concepts from **Chapter 9: Deployability, Portability, and Containers**.

---

## Project Structure

### Part 1: Deployability and Architecture

#### 1.1 Deployability Assessment (`part1_deployability_assessment.md`)

* Identified problems in current system:

  * Manual deployments (SSH)
  * Host differences (snowflake VMs)
  * Config stored in files
  * Downtime during updates
  * Local disk usage for uploads
* Proposed solutions using Kubernetes:

  * Immutable container images
  * Rolling updates
  * ConfigMaps and Secrets
  * Health checks
  * External storage

---

#### 1.2 Architecture Diagram (`part1_architecture_before_after.drawio`, `.png`)

* Compared **Before vs After architecture**

**Before:**

* Monolith on VM
* Local uploads (`/var/citybite/uploads`)
* Manual config

**After:**

* Kubernetes (EKS)

* API Deployment + Worker Deployment

* Ingress → Service → Pods

* S3 / PVC for uploads

* Managed PostgreSQL

* Included:

  * Data flow paths
  * Legend

---

## Part 2: Containers and Runtime

#### 2.1 Container Specification (`part2_container_spec.md`)

* Defined container setup for:

  * Order API
  * Background Worker

Key points:

* Base image: `python:3.11-slim`
* Environment variables:

  * `PORT`, `DATABASE_URL`, `LOG_LEVEL`, `AWS_REGION`, `DATA_DIR`
* Logs go to **stdout**
* One process per container
* Included Dockerfile sketch

---

#### 2.2 Health and Rollout (`part2_health_and_rollout.md`)

* Defined Kubernetes probes:

  * **Liveness** → restart container
  * **Readiness** → control traffic

* Rolling update process:

  * v1.4.0 → v1.5.0
  * Zero downtime using rolling strategy

* Failure handling:

  * Detect using logs and metrics
  * Rollback using:

    ```
    kubectl rollout undo deployment/citybite-api
    ```

---

## Part 3: Portability and Delivery

#### 3.1 Portability and State (`part3_portability_and_state.md`)

* Compared storage options:

  * PVC vs S3 → **S3 recommended**

* Secrets management:

  * Kubernetes Secrets + AWS Secrets Manager

* Database:

  * Managed PostgreSQL (RDS) outside cluster
  * Connected using `DATABASE_URL`

* Dev/Prod parity:

  * Docker Compose for local setup
  * Same env variables and structure

---

#### 3.2 Delivery Sequence (`part3_delivery_sequence.drawio`, `.png`)

* Sequence diagram from **code commit to running pods**

Participants:

* Developer
* GitHub
* CI Runner
* Container Registry
* Kubernetes Control Plane
* Node
* Pod

Flow includes:

* Build and push image
* Tag promotion (git SHA → v1.5.0)
* Deployment to Kubernetes
* Pod startup and readiness

Failure cases:

* Image pull error
* Readiness failure
* Rollback to previous version

---

## Key Improvements

After migration, CityBite achieves:

* Faster and safer deployments
* No downtime during updates
* Better scaling during traffic spikes
* Secure and flexible configuration
* Portable system across environments

---

## Conclusion

This project shows how modern container and Kubernetes practices improve a real-world system like CityBite.
By using **containers, environment-based config, and Kubernetes features**, we solve many problems from the old VM-based setup.
