# Assignment Submission: Lecture 3

**Student Name**: Hadiya Shreyash Rameshbhai\
**Student ID**: 30009058\
**Submission Date**: 22-04-2026

## Overview

Migration of the **CityBite** food-ordering monolith from hand-managed EC2 VMs to a containerized deployment on **Amazon EKS** (`eu-west-1`). Covers deployability analysis, container image spec, rollout strategy, state/secrets handling, and the end-to-end delivery flow.

## Files Included

- `part1_deployability_assessment.md` -- Five VM bottlenecks mapped to Kubernetes mitigations + observability trade-off
- `part1_architecture_before_after.drawio` / `.png` -- Before (Pets-on-VMs) vs After (EKS) architecture
- `part2_container_spec.md` -- Base image choice, layered build, 12-factor runtime, full Dockerfile
- `part2_health_and_rollout.md` -- Liveness/Readiness probes, rolling update, `kubectl rollout undo`
- `part3_portability_and_state.md` -- EFS vs S3, External Secrets Operator, RDS, Docker Compose parity
- `part3_delivery_sequence.drawio` / `.png` -- CI/CD sequence diagram with failure branch

## Key Highlights

- Immutable container images + RollingUpdate for zero-downtime deploys
- Readiness probes (`SELECT 1` on RDS, EFS writable-check) gate bad releases automatically
- Secrets synced from AWS Secrets Manager via External Secrets Operator; RDS kept outside the cluster

## How to View

1. Open `.drawio` files in draw.io (app.diagrams.net) to edit diagrams.
2. View `.png` files for quick diagram previews.
3. Read `.md` files for all documentation.
4. (Optional) Run Python code examples in the `code/` directory.
