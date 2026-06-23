# Assignment Submission: Lecture 9

**Student Name**: Arda Arslan
**Student ID**: 30008610
**Submission Date**: 16/04/2026

## Overview

This submission documents the migration of CityBite from a VM-based monolith to a Kubernetes-based architecture. It covers deployability improvements, container design, rollout strategy, portability, and the delivery pipeline.

## Files Included

* `part1_deployability_assessment.md` — Deployability risks and Kubernetes-based mitigations
* `part1_architecture_before_after.drawio` — Before/after architecture diagram (draw.io)
* `part1_architecture_before_after.png` — Before/after architecture diagram (image)
* `part2_container_spec.md` — Container image design and runtime contract
* `part2_health_and_rollout.md` — Liveness/readiness, rolling update, and rollback strategy
* `part3_portability_and_state.md` — Storage, secrets, database, and portability decisions
* `part3_delivery_sequence.drawio` — CI/CD delivery sequence diagram (draw.io)
* `part3_delivery_sequence.png` — CI/CD delivery sequence diagram (image)
* `README.md` — This file

## Key Highlights

* Designed a Kubernetes-based deployment using **AWS EKS**
* Used **CI-built container images** with version promotion (git SHA -> release tag)
* Defined a **rolling update strategy** with readiness-based traffic control

## How to View

1. Open `.drawio` files in draw.io to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files for documentation
