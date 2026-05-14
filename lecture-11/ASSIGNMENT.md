# Assignment: CityBite Always Open — Availability & Services

## Overview

You **document how CityBite stays available** (same fictional product as Lectures 9–11) using **Chapter 11: Availability and Services**: components vs **services** you depend on, **SLOs/SLIs**, **monitoring**, **cascading failure** controls (**circuit breaker**, **timeouts**, **bulkhead**), **replication**, and optional **event-sourcing** for critical workflows.

Assume the **Kubernetes** + **Postgres** baseline from Lecture 9 and the **scale** story from Lecture 10. This assignment is **design + narrative + diagrams** — no production cluster required.

Align vocabulary with **`example1_availability_circuit_breaker_citybite.py`** (circuit breaker / retries) and **`example2_availability_monitoring_citybite.py`** (readiness vs shallow health).

---

## Learning Objectives

By completing this assignment, you will:

- Separate **components you operate** from **services** operated by others — and state trust boundaries  
- Define at least one **SLO** with a measurable **SLI** for CityBite  
- Propose **monitoring** that distinguishes process health from **user-visible** availability  
- Explain how **retries** can harm availability and how **circuit breakers** / **canaries** mitigate risk  
- Describe **replication** (sync vs async) for Postgres or read models and name **consistency** trade-offs  

---

## Baseline (given)

| Aspect | Today |
|--------|--------|
| Product | CityBite — customers, restaurants, dispatch |
| Runtime | K8s, Order API Deployment, workers, managed **Postgres**, CDN/object storage |
| Dependencies | **Payment gateway** SaaS, **maps/routing** API, SMS/push provider |
| Pain | Partner outage or slow gateway → **retry storms**; “green” pods that cannot reach DB; Friday incidents with unclear **blast radius** |

Your design must address **at least four** distinct availability risks with **named** mechanisms (not only “add redundancy”).

---

## Part 1: Services map & SLOs

### Task 1.1: Components vs services inventory

**Objective:** List what CityBite **owns** vs what is a **remote service**.

**Requirements:**

1. Table with **at least six** rows: **name**, **component or external service**, **who operates**, **connector** (HTTPS, queue, …), **main risk if unavailable**.  
2. Mark **two** dependencies where you would insist on a **formal SLA** or exit plan (vendor bankruptcy, breaking API).  
3. One paragraph: **why** availability of external APIs is a **product** risk, not only an IT risk.

**Deliverable:** `part1_services_inventory.md`

**Grading:** 28 points

---

### Task 1.2: SLI / SLO / error budget

**Objective:** Make availability **measurable**.

**Requirements:**

1. Pick **one** user journey (e.g. “place paid order” or “restaurant marks order ready”).  
2. Define **one SLI** (ratio or latency threshold you can measure from logs/metrics).  
3. Define **one SLO** (target over a month, e.g. 99.5% successful checkouts).  
4. Explain **error budget** — what happens when burn rate is high (freeze features, freeze deploys, etc.).

**Deliverable:** `part1_slo_error_budget.md`

**Grading:** 22 points

---

## Part 2: Monitoring & failure containment

### Task 2.1: Monitoring & probes

**Objective:** Tie **lecture examples** to Kubernetes and dashboards.

**Requirements:**

1. Describe **liveness** vs **readiness** for the Order API — paths, what each proves, **failure** action (restart vs remove from LB).  
2. Contrast with **`example2`** — why “200 OK on `/healthz`” can **lie** under pool exhaustion.  
3. **Synthetic check** — one black-box probe you would run from outside the cluster (what it asserts).  
4. **Alerting** — two alerts with clear **threshold** and **runbook** first step.

**Deliverable:** `part2_monitoring_probes.md`

**Grading:** 30 points

---

### Task 2.2: Cascading failures & circuit breaker

**Objective:** Show you understand **amplification** and **containment**.

**Requirements:**

1. Narrative: payment gateway **500** + client **retry storm** — how CityBite’s own API degrades (**cite `example1`** themes).  
2. **Circuit breaker** policy: thresholds, open duration, fallback (e.g. “pay later”, queue order, decline with clear UX) — **one** paragraph each.  
3. **Timeouts & bulkhead** — thread pool or connection limits per dependency — why they pair with breakers.  
4. **Canary request** (lecture pattern) — **one** use case in CityBite (e.g. suspicious payload to one worker first) — optional if not applicable, explain **why not**.

**Deliverable:** `part2_cascading_failures.md`

**Grading:** 25 points

---

## Part 3: Replication & optional event log

### Task 3.1: Data redundancy

**Objective:** Connect **replication** to availability.

**Requirements:**

1. For **Postgres**: **sync vs async** replica — which you use for **reporting** vs **failover**, and **RPO** intuition.  
2. **Split-brain** or stale read — **one** paragraph on what goes wrong if failover is misconfigured.  
3. **CAP** at high level — when you choose **availability** over **strong consistency** for a **read** path (e.g. ETA display).

**Deliverable:** `part3_replication_cap.md`

**Grading:** 25 points

---

### Task 3.2: Diagram — steady vs failure

**Objective:** Visualize normal path vs **dependency failure** path.

**Requirements:**

1. **draw.io**: left **steady** (happy path checkout); right **failure** (gateway slow → breaker open → fallback path).  
2. Numbered flows (1–4 minimum), **legend**, title block.  
3. Export **`part3_diagram_steady_vs_failure.png`** alongside `.drawio`.

**Deliverables:** `part3_diagram_steady_vs_failure.drawio` + `.png`

**Grading:** 20 points

---

### Task 3.3 (optional +8 bonus): Event sourcing sketch

**Objective:** Show when an **append-only event log** helps recovery or audit.

**Requirements:** ≤ 1 page — **one** bounded context (e.g. order state), **events** list, how replay helps after bug — **not** full implementation.

**Deliverable:** `part3_event_sourcing_bonus.md`

**Grading:** +8 bonus (max course score cap still applies)

---

## Deliverables checklist

| File | Part |
|------|------|
| `part1_services_inventory.md` | 1.1 |
| `part1_slo_error_budget.md` | 1.2 |
| `part2_monitoring_probes.md` | 2.1 |
| `part2_cascading_failures.md` | 2.2 |
| `part3_replication_cap.md` | 3.1 |
| `part3_diagram_steady_vs_failure.drawio` | 3.2 |
| `part3_diagram_steady_vs_failure.png` | 3.2 |
| `part3_event_sourcing_bonus.md` | 3.3 (optional) |

**Total: 150 points** (+8 optional bonus)

---

## Submission

GitHub Pull Request per `../lecture-3/SUBMISSION_GUIDE.md`.  
Suggested PR title: `Assignment Lecture 11: CityBite availability — <Your Name>`
