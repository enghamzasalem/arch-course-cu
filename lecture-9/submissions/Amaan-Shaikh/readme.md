# Assignment Submission: Lecture 9

**Student Name**: Amaan Shaikh

## Overview

This submission documents the migration of CityBite from a VM-based monolith to a Kubernetes-based architecture. It covers deployability improvements, container design, rollout strategy, portability, and the delivery pipeline.

## Files Included

### Part 1 – Deployability

- `part1_deployability_assessment.md` — 5 deployability risks and Kubernetes-based mitigations
- `part1_architecture_before_after.drawio` — Before/after architecture diagram (draw.io)
- `part1_architecture_before_after.png` — Before/after architecture diagram (image)

### Part 2 – Containers

- `part2_container_spec.md` — Container image design (Python slim, non-root user) and runtime contract
- `part2_health_and_rollout.md` — Liveness/readiness probes, rolling update, and rollback strategy

### Part 3 – Portability and Delivery

- `part3_portability_and_state.md` — Storage (S3), secrets, database, and dev/prod parity decisions
- `part3_delivery_sequence.drawio` — CI/CD delivery sequence diagram (draw.io)
- `part3_delivery_sequence.png` — CI/CD delivery sequence diagram (image)

### Documentation

- `README.md` — This file

## Key Highlights

- Designed a Kubernetes-based deployment using **AWS EKS**
- Used **CI-built container images** with version promotion (git SHA → release tag)
- Defined a **rolling update strategy** with readiness-based traffic control
- **Object storage (S3)** for menu uploads – shared, durable, CDN-ready
- **Secrets** in AWS Secrets Manager + Kubernetes Secrets
- Managed PostgreSQL **outside the cluster** (RDS)

## Migration Summary

| Aspect | Before (VM) | After (K8s) |
|--------|-------------|-------------|
| Deploy | Manual SSH | CI + kubectl |
| Config | .env on disk | Env vars + Secrets |
| Uploads | Local disk | S3 object storage |
| Rollback | Minutes | Instant (kubectl undo) |
| Scaling | Vertical only | Horizontal (replicas) |

## How to View

1. Open `.drawio` files in [draw.io](https://app.diagrams.net/) to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files in any text editor or Markdown viewer