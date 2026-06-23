# Lecture 9 — CityBite Deployment (Kubernetes)
**Student Name**:Khaoula Adouli
**Submission Date**: 16/04/2026

## Overview

This assignment presents the transformation of the CityBite system from a VM-based architecture to a containerized deployment on Kubernetes (AWS EKS).

The goal is to improve:

* deployability
* portability
* scalability
* reliability

---

## Contents

### Part 1 — Deployability Assessment

* Analysis of the initial VM-based system
* Identification of deployment issues
* Comparison with Kubernetes-based architecture
* Architecture diagram (before vs after)

---

### Part 2 — Containers and Deployment

* Container specification for all services
* Configuration management (ConfigMap and Secrets)
* Health checks (liveness, readiness, startup)
* Rolling update and rollback strategy

---

### Part 3 — Portability and State

* Portability across environments (dev, CI, production)
* Stateless vs stateful design
* External data management (Amazon RDS, Redis)
* Delivery sequence diagram (CI/CD pipeline)

---

## Architecture Summary

The final architecture is based on:

* Kubernetes (AWS EKS)
* Docker containers
* Amazon ECR (container registry)
* Amazon RDS (PostgreSQL database)
* Redis (cache)

---

## Key Design Decisions

* Stateless application containers for scalability
* External database for persistence
* Configuration externalization using ConfigMaps and Secrets
* Automated deployment using CI/CD pipeline

---

## Submitted Files

The submission includes the following files:

- part1_deployability_assessment.md  
- part1_architecture_before_after.drawio  
- part1_architecture_before_after.png  

- part2_container_spec.md  
- part2_health_and_rollout.md  

- part3_portability_and_state.md  
- part3_delivery_sequence.drawio  
- part3_delivery_sequence.png  

- README.md

---

## Conclusion

The migration to Kubernetes improves deployment speed, reliability, and scalability, while ensuring portability across environments.
