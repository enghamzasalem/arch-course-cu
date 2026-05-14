# Assignment: CityBite on Kubernetes — Deployability, Portability, and Containers

## Overview

You **document an architecture** for moving **CityBite** (regional food delivery, same fictional product as the lecture examples) from **pets-on-VMs** to **Kubernetes** on a public cloud. You apply **Chapter 9: Deployability, Portability, and Containers**: repeatable deploys, portable configuration, container boundaries, and safe rollouts.

**Real-world product context**

- **CityBite** — mobile apps for customers, tablet app for restaurant partners, dispatch dashboard for operations.
- **Today (baseline):** a **monolith** (order API + background jobs) on **long-lived VMs**, deploys via SSH scripts, config files edited on each host, menu images on local disk, Postgres on a single managed instance.
- **Goal:** **containerized** services on **Kubernetes** (EKS, GKE, or AKS — pick one in your doc), **CI-built images**, **environment-based config**, clear **health** and **storage** strategy.

You **do not** need a running cluster. You submit **markdown + diagrams** (and optional sketch snippets such as Dockerfile fragments in markdown code fences).

---

## Learning Objectives

By completing this assignment, you will:

- Relate **deployability** goals to concrete platform choices (CI, images, rollouts)
- Specify **container** images and runtime contracts (env vars, ports, signals)
- Address **portability** across laptop → CI → cluster (paths, secrets, databases)
- Design **observability** hooks (logs, metrics, probes) appropriate for orchestrators
- Communicate trade-offs to **non-developers** (ops, PM) in writing

---

## Baseline (given) — current production pain

Use this narrative consistently across your files:

| Aspect | Today |
|--------|--------|
| Deploy | Manual SSH; **snowflake** hosts differ slightly |
| Config | `.env` files on disk per VM; secrets sometimes in git history |
| Traffic | Evening **dinner spikes**; occasional marketing push |
| Data | **PostgreSQL** (RDS-like); menu **JPEGs** on VM disk under `/var/citybite/uploads` |
| Outages | Restart monolith → **minutes** of partial downtime |

Your design should **fix or mitigate** at least three distinct pain points with explicit mechanisms (e.g. rolling updates, `PORT`, volume for uploads, external secrets).

---

## Reference — environment variables (align with lecture examples)

These names appear in **`example1_deployability_citybite_api.py`** and **`example2_portability_menu_uploads.py`**. You may extend the set in your design, but stay consistent.

| Variable | Purpose (example) |
|----------|-------------------|
| `PORT` | HTTP bind port injected by the platform |
| `DATABASE_URL` | Connection string (dev SQLite vs prod Postgres) |
| `LOG_LEVEL` | e.g. `INFO`, `DEBUG` |
| `AWS_REGION` / `GCP_*` / `AZURE_*` | Your chosen cloud — pick **one** vendor for the whole assignment |
| `DATA_DIR` | Writable root for **menu uploads** (volume mount in K8s) |

---

## Part 1: Deployability and target architecture

### Task 1.1: Deployability assessment

**Objective:** Explain where today’s model hurts **deployability** and what you will change.

**Requirements:**

1. List **at least five** deployability risks or bottlenecks tied to the **baseline** (e.g. host drift, coupling to disk layout, slow rollbacks, unclear ownership of config).
2. For each, propose **one** mitigation that Kubernetes + containers typically enable (be specific: e.g. “immutable image digest pinned in Deployment”, not only “use K8s”).
3. State **one** thing that becomes **harder** after the move (e.g. local repro of distributed issues) and how you mitigate it.

**Deliverable:** `part1_deployability_assessment.md`

**Grading:** 30 points

---

### Task 1.2: Architecture diagram (before vs after)

**Objective:** Show how pieces move from VMs to cluster.

**Requirements:**

1. **draw.io** diagram: **left** — baseline (monolith on VM, DB, uploads path); **right** — target (e.g. Deployment for API, optional Job/CronJob or second Deployment for workers, Service, Ingress, PVC or object storage for uploads, managed DB).
2. **Labels:** at least **two** data paths (e.g. “HTTPS → Ingress → Service → Pod”, “upload → volume / S3”).
3. **Legend**.

**Deliverables:** `part1_architecture_before_after.drawio` + `.png`

**Grading:** 20 points

---

## Part 2: Containers and runtime contract

### Task 2.1: Container images and process model

**Objective:** Define how **CityBite Order API** (and optionally a **background worker** for dispatch retries) runs in containers.

**Requirements:**

1. **Images:** For the API (required) and worker (optional): base image choice (e.g. official Python slim), **why**; list **build steps** at a high level (dependency install, copy app, non-root user if applicable).
2. **Runtime contract:** document required **env vars** (use the reference table + any you add), **listening port** (`PORT`), how **logs** leave the container (stdout / sidecar — justify).
3. **Single responsibility:** one main process per container, or justify an exception.
4. Include a **short** `Dockerfile`-style sketch **in markdown** (10–25 lines) for the API image only — it does not need to build on the grader’s machine.

**Deliverable:** `part2_container_spec.md`

**Grading:** 25 points

---

### Task 2.2: Health, rollout, and failure

**Objective:** Connect Chapter 9 ideas to **Kubernetes** operations.

**Requirements:**

1. Define **liveness** vs **readiness** probes for the Order API (paths or TCP, thresholds — be plausible).
2. Describe a **rolling update** from image `v1.4.0` → `v1.5.0`: what the cluster does, what happens if the new pods fail readiness.
3. **Real incident tie-in:** one short paragraph on how you would detect and roll back a bad deploy (metrics, previous ReplicaSet, `kubectl rollout undo` — names may match your cloud).

**Deliverable:** `part2_health_and_rollout.md`

**Grading:** 15 points

---

## Part 3: Portability, data, and pipeline

### Task 3.1: Portability and state

**Objective:** Ensure the design works across **dev laptop**, **CI**, and **prod cluster**.

**Requirements:**

1. **Menu uploads:** choose **PVC + `DATA_DIR`** **or** **object storage (e.g. S3)** — compare **two** pros/cons for CityBite (cost, backup, complexity).
2. **Secrets:** where API keys for payment and DB passwords live in the target architecture (Kubernetes Secret + external store, etc.) — **not** in the image layer.
3. **Database:** keep managed Postgres **outside** the cluster or justify a different pattern; describe connection from pods (`DATABASE_URL` injection).
4. **Dev/prod parity:** one paragraph on how developers run **similar** containers locally (e.g. `docker compose` with volume for `DATA_DIR`).

**Deliverable:** `part3_portability_and_state.md`

**Grading:** 20 points

---

### Task 3.2: Delivery sequence

**Objective:** Show the path from commit to running pods.

**Requirements:**

1. **Sequence diagram** (draw.io): **≥6** participants (e.g. Developer, GitHub, CI runner, Container registry, Kubernetes control plane, Pod). Include **image tag** promotion (e.g. `git sha` → `:v1.5.0`).
2. At least **one** failure branch (e.g. image pull error or failed readiness) with what happens next.

**Deliverables:** `part3_delivery_sequence.drawio` + `.png`

**Grading:** 10 points

---

## Submission Requirements

### Submission method

GitHub Pull Request — see `../lecture-3/SUBMISSION_GUIDE.md`.

### File layout

```
submissions/YOUR_NAME/
├── part1_deployability_assessment.md
├── part1_architecture_before_after.drawio
├── part1_architecture_before_after.png
├── part2_container_spec.md
├── part2_health_and_rollout.md
├── part3_portability_and_state.md
├── part3_delivery_sequence.drawio
├── part3_delivery_sequence.png
└── README.md
```

### Diagrams

Submit **both** `.drawio` and `.png` for every diagram.

---

## Grading rubric

| Part | Task | Points |
|------|------|--------|
| Part 1 | Deployability assessment | 30 |
| Part 1 | Before/after architecture diagram | 20 |
| Part 2 | Container spec + Dockerfile sketch | 25 |
| Part 2 | Health probes + rollout / rollback | 15 |
| Part 3 | Portability, uploads, secrets, DB | 20 |
| Part 3 | Delivery sequence diagram | 10 |
| **Total** | | **120** |

### Quality criteria

- **Realism:** CityBite constraints (spikes, uploads, partners) show up in decisions
- **Consistency:** Same component names and env vars across files
- **Operability:** Another engineer could implement your spec without guessing

---

## Getting started

1. Run **`example1_deployability_citybite_api.py`** and **`example2_portability_menu_uploads.py`**.
2. Watch for **read-only root filesystem** and **ephemeral container disk** when you design uploads.
3. Pick **one** cloud + **one** Kubernetes distribution and stick to it for all parts.

---

## Deadline

**Due date:** [To be announced by instructor]

**Submission:** GitHub Pull Request to `arch-course-cu/lecture-9/submissions/YOUR_NAME/`

Good luck.
