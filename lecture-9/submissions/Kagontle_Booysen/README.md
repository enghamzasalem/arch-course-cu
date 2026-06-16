# Assignment Submission: CityBite on Kubernetes
**Student Name**: Kagontle Booysen
**Student ID**: 30009255
**Submission Date**: 16 April 2026

---

## Overview
This submission documents a full migration architecture for CityBite — a regional food delivery platform — from a monolithic VM-based deployment to a containerised, Kubernetes-native architecture on Amazon EKS. The work covers deployability assessment, container design, health and rollout strategy, portability and state management, and a CI/CD delivery pipeline with failure handling.

---

## Files Included

| File | Description |
|---|---|
| `part1_deployability_assessment.md` | Five deployability risks in the current VM baseline, Kubernetes mitigations for each, and one thing that becomes harder after migration |
| `task1_2_architecture_diagram.md` | Mermaid code for before/after architecture diagrams (baseline VMs vs EKS target) |
| `part2_container_spec.md` | Container image design, Dockerfile sketch, runtime contract (env vars, port, log strategy), single-responsibility justification |
| `part2_health_and_rollout.md` | Liveness, readiness, and startup probe definitions; rolling update sequence v1.4.0 → v1.5.0; incident detection and rollback procedure |
| `part3_portability_and_state.md` | Menu uploads storage comparison (EFS PVC vs S3), secrets management chain, managed RDS connection pattern, dev/prod parity via Docker Compose |
| `part3_delivery_sequence.drawio` | Editable draw.io sequence diagram: 7 participants, happy path, failure branch, rollback |
| `part3_delivery_sequence.png` | PNG export of the delivery sequence diagram |

---

## Key Highlights

- **Zero-downtime deploys** enforced by `RollingUpdate` with `maxUnavailable: 0` and readiness probe gating — no customer traffic is dropped during any rollout or rollback
- **Full secrets chain documented** from AWS Secrets Manager → ASCP → Kubernetes Secret → pod environment variable; no secret ever touches an image layer or version control
- **Dev/prod parity** achieved through a Docker Compose stack using the same image, the same environment variable names (`PORT`, `DATABASE_URL`, `DATA_DIR`, `LOG_LEVEL`, `AWS_REGION`), and the same filesystem mount path — only the injected values differ between laptop and cluster
- **Failure branch fully traced** in the delivery sequence: stalled rollout → CloudWatch alarm → PagerDuty → `kubectl rollout undo` → zero-downtime recovery from ECR-retained image digest

---

## How to View

1. Open `part3_delivery_sequence.drawio` in [draw.io](https://app.diagrams.net) (**Extras → Edit Diagram** to inspect XML) for the editable delivery sequence diagram
2. View `part3_delivery_sequence.png` for a quick reference of the delivery sequence
3. Paste the Mermaid code blocks in `task1_2_architecture_diagram.md` into [mermaid.live](https://mermaid.live) to render the before/after architecture diagrams
4. Read all `.md` files for full documentation — no build step required
5. Code sketches (Dockerfile fragments, YAML snippets) in `part2_container_spec.md` and `part2_health_and_rollout.md` are illustrative and reference `python:3.12-slim` — runnable with Docker and a valid `requirements.txt`

---

## Environment Variable Reference

| Variable | Purpose | Source in K8s |
|---|---|---|
| `PORT` | HTTP bind port | ConfigMap |
| `DATABASE_URL` | Postgres connection string | Secret (AWS Secrets Manager) |
| `LOG_LEVEL` | Logging verbosity | ConfigMap |
| `DATA_DIR` | Writable root for menu uploads | ConfigMap (must match EFS PVC mountPath) |
| `AWS_REGION` | Target AWS region | ConfigMap |

---

## Cloud Platform
All target architecture components use **Amazon Web Services (AWS)**: EKS (cluster), ECR (image registry), EFS (shared uploads volume), RDS PostgreSQL Multi-AZ (database), Secrets Manager (credential store), CloudWatch (observability).
