# Assignment: CityBite at Peak — Scalability Architecture

## Overview

You **document a scalability architecture** for **CityBite** (regional food delivery, same product as Lectures 9–10). You apply **Chapter 10: Scalability**: workloads vs resources, horizontal scaling, bottlenecks, caching, partitioning, and realistic **capacity** trade-offs.

Assume the **Kubernetes** baseline from Lecture 9 exists (containerized API, workers, managed Postgres, object storage or PVC for uploads). This assignment asks **how it behaves under growth** and what you add when the **dinner rush** or a **marketing campaign** pushes traffic and data volume.

You **do not** need a running load test in the cluster. You submit **markdown + diagrams** (and optional formulas or tables). If you run local benchmarks, you may cite them briefly.

---

## Learning Objectives

By completing this assignment, you will:

- Name **workload dimensions** that grow for CityBite and map them to **resource** needs
- Choose between **scale up** and **scale out** for at least three subsystems and justify each
- Identify **serial bottlenecks** (especially the database) and propose **architectural** mitigations
- Explain **cache** and **queue** roles using vocabulary from the lecture examples
- Communicate **limits** and **degradation** behavior to non-developers (product, ops)

---

## Baseline (given) — capacity context

Use this narrative consistently across your files:

| Aspect | Context |
|--------|---------|
| Traffic | Evening **dinner spikes**; occasional **marketing** pushes (coupons, free delivery hour) |
| Product | Mobile customers, restaurant tablets, dispatch dashboard |
| Data | **PostgreSQL** for orders and accounts; **menu images** in object storage or PVC |
| Compute | **Order API** Deployment; optional **notification worker** (from Lecture 9 story) |
| Pain | **p95 latency** rises under load; **DB CPU** high; **connection pool** exhaustion; **duplicate** heavy queries per restaurant |

Your design should address **at least four** distinct scalability risks with concrete mechanisms (e.g. “read replica for restaurant reporting”, “SQS + autoscaled workers”, **not** only “add more servers”).

Align terminology with **`example1_scalability_hot_path_citybite.py`** (hot path / indexing / partition key) and **`example2_scalability_queue_workers_citybite.py`** (decouple checkout from outbound I/O).

---

## Part 1: Workload model and bottlenecks

### Task 1.1: Workload dimensions

**Objective:** State what grows for CityBite and how you measure it.

**Requirements:**

1. List **at least five** workload dimensions (e.g. concurrent customers, orders per minute, restaurants onboarded, menu image bytes, dispatch dashboard queries).
2. For each dimension, name the **resource** that typically saturates first (CPU, RAM, disk IOPS, network egress, DB connections, application locks, …).
3. Pick **one** “hero scenario” (e.g. **Friday 19:00–21:00** in one city) and describe **qualitatively** how the system should feel to users if scaled well vs poorly.

**Deliverable:** `part1_workload_and_bottlenecks.md`

**Grading:** 28 points

---

### Task 1.2: Scale up vs scale out decision log

**Objective:** Show you can choose vertical vs horizontal scaling deliberately.

**Requirements:**

1. Create a table with **at least four** rows (subsystems): e.g. Order API pods, notification workers, Postgres, object storage / CDN.
2. Columns: **subsystem**, **primary bottleneck**, **scale up** option, **scale out** option, **your choice** for Year 1, **one sentence why**.
3. Include **one** explicit “**does not scale infinitely**” note (e.g. single-writer OLTP primary, operational cost of shards).

**Deliverable:** `part1_scale_decisions.md` (or a section inside 1.1 if you prefer one file — if combined, make sections clearly titled)

**Grading:** 22 points

---

## Part 2: Architecture under growth

### Task 2.1: Data plane — reads, writes, caches

**Objective:** Apply Chapter 10 ideas to CityBite’s **data** path.

**Requirements:**

1. Describe **write path** for **new order** (API → DB → any outbox/event). State what must stay **strongly consistent** vs what can be **eventually** consistent (notifications, analytics).
2. Describe **read path** for **kitchen active orders** (tie to **partition key / index** thinking from `example1`).
3. Propose **at least one** cache (what key, what TTL or invalidation strategy, what happens on stale read). Connect to a real CityBite screen (customer or restaurant).
4. **Queue** or stream: reference **`example2`** — where would you **not** block the HTTP response?

**Deliverable:** `part2_data_scaling.md`

**Grading:** 30 points

---

### Task 2.2: Diagram — steady vs peak

**Objective:** Visualize how traffic and data move at normal load vs peak.

**Requirements:**

1. **draw.io** diagram with two swimlanes or two panels: **steady** vs **peak** (add components only used under peak if any: e.g. read replica, Redis, HPA extra pods, queue depth).
2. **Labels:** at least **three** numbered flows (e.g. “1 HTTPS → Ingress”, “2 read menu cache”, “3 write order primary”).
3. **Legend** and **title** block with your name / date (as your course requires).

**Deliverables:** `part2_architecture_steady_vs_peak.drawio` + exported **`part2_architecture_steady_vs_peak.png`**

**Grading:** 25 points

---

## Part 3: Patterns, limits, and operations

### Task 3.1: Pattern checklist

**Objective:** Map textbook-style patterns to CityBite.

**Requirements:**

1. For **each** of the following, **one short paragraph** (3–6 sentences): how CityBite would use it, or why it is **not** the first choice yet — **load balancing**, **sharding/partitioning**, **scatter/gather**, **master/worker** (or worker pool).
2. Explicitly mention **multi-tenant** fairness: e.g. one viral restaurant must not starve others (even at a high level).

**Deliverable:** `part3_patterns.md`

**Grading:** 20 points

---

### Task 3.2: Autoscaling and backpressure

**Objective:** Connect Kubernetes **HPA** (or equivalent) to **measurable** signals.

**Requirements:**

1. Propose **one** HPA rule for the Order API: metric (e.g. CPU, RPS proxy, custom metric), target, **min/max** replicas — plausible numbers, labeled as assumptions.
2. Describe **one** backpressure or degradation policy when downstream fails (e.g. queue depth limit, 503 with `Retry-After`, disable non-critical features).
3. **Failure lesson:** 5–8 sentences on what happens if you only scale **stateless** pods but **forget** the database (symptoms, detection, mitigation).

**Deliverable:** `part3_autoscaling_and_limits.md`

**Grading:** 25 points

---

## Deliverables checklist

| File | Part |
|------|------|
| `part1_workload_and_bottlenecks.md` | 1.1 |
| `part1_scale_decisions.md` | 1.2 |
| `part2_data_scaling.md` | 2.1 |
| `part2_architecture_steady_vs_peak.drawio` | 2.2 |
| `part2_architecture_steady_vs_peak.png` | 2.2 |
| `part3_patterns.md` | 3.1 |
| `part3_autoscaling_and_limits.md` | 3.2 |

**Total: 150 points**

---

## Academic integrity

- Cite any **external** sources (blog, vendor doc) with URL and date accessed.
- **AI tools:** follow your course policy; if allowed with disclosure, state briefly what you used and how you verified technical claims.

---

## Submission

GitHub Pull Request to the course repository per `../lecture-3/SUBMISSION_GUIDE.md`.  
PR title suggestion: `Assignment Lecture 10: CityBite scalability — <Your Name>`
