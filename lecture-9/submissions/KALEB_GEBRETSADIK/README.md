# Assignment Submission: Lecture 9 - Deployability, Portability, and Containers

**Student Name**: Kaleb Gebretsadik  
**Student ID**: 30008744  
**Submission Date**: April 19, 2026

## Overview

This submission explicitly outlines the complete architectural transition of **CityBite** from a legacy Pets-on-VMs architecture over to a highly deployable, containerized stack hosted safely on **Kubernetes (AWS EKS)**. By utilizing isolated Docker containers, dynamic environment configuration mappings, external Amazon S3 Object Storage, and standardized network health probes, this documentation effectively resolves baseline limitations regarding scaling capacity, rollout safety, and host-drift risks.

## Files Included

### Part 1: Deployability and Target Architecture
- `part1_deployability_assessment.md`: Highlights exactly 5 critical operational bottlenecks (like VM drift and manual SSH pain) and details precise K8s-based container mitigations.
- `part1_architecture_before_after.drawio`: Visual diagram mapping the physical components shifting from monolithic local disk architecture over to AWS Load Balancers, K8s Pods, and S3 APIs. 
- `part1_architecture_before_after.png`: Standard PNG export of the component transition.

### Part 2: Containers and Runtime Contract
- `part2_container_spec.md`: Documents base image reasoning (`python:3.11-slim`), single-responsibility bounds, the requisite 12-factor environment injections, and a fully functional sample JSON structured `Dockerfile`.
- `part2_health_and_rollout.md`: Explicitly designs the TCP/HTTP endpoints utilized for Liveness/Readiness probes and describes a zero-downtime rolling update process alongside declarative incident rollbacks.

### Part 3: Portability, Data, and Pipeline
- `part3_portability_and_state.md`: Validates exactly how Amazon S3 removes state from Pod footprints securely, traces the use of AWS Secrets Manager / K8s Secrets abstractions, and resolves local Dev/Prod parity through Docker Compose.
- `part3_delivery_sequence.drawio`: A standard UML sequence diagram tracking commit execution paths traversing CI pipelines directly into Kubelet node pulling mechanisms (including an explicit probe-failure scenario mapped).
- `part3_delivery_sequence.png`: Standard PNG export of the delivery sequence.

## Key Highlights

- **External State Removal:** Completely isolating local `/var/citybite/uploads` constraints smoothly converting over natively to Amazon S3 API streams.
- **Fail-Safe Rollout Execution:** Integrating robust Readiness Probes protecting the K8s Service layer, rendering aggressive downtime instances to practically zero.
- **Immutable Parity:** Eliminating "Snowflake server" VM drift by securing local laptop CI tests with 100% production-equivalent `linux/amd64` minimal Docker image environments.

## How to View

1. **Read `.md` files** for theoretical implementations and decisions.
2. **Open `.drawio` files** in [app.diagrams.net](https://app.diagrams.net/) to explore or tweak the editable workflow paths.
3. **Double-check `.png` files** for easy diagram evaluation.
