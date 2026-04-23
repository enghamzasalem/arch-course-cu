# Part 1.2 — Scale up vs scale out (Year-1 decision log)

**Context:** CityBite on Kubernetes, PostgreSQL, object storage; dinner spikes and marketing pushes. Goal: **deliberate** vertical vs horizontal choices per subsystem.

| Subsystem | Primary bottleneck (first signal) | Scale up option | Scale out option | **Year-1 choice** | One-sentence why |
|-----------|-----------------------------------|-----------------|------------------|-------------------|------------------|
| **Order API** (HTTP) | CPU, thread pool, p95 at ingress | Larger pod requests/limits, bigger node type | **More pod replicas** behind **Service** + HPA, spread across nodes | **Scale out** (replicas + **HPA**) | Stateless request handling gains linearly from **horizontal** pod replicas until DB or pool limits. |
| **Notification / async workers** | Event backlog, `notify` IOPS to providers | Bigger worker pods, more connections per process | **More worker replicas** or KEDA on **queue depth**; separate Deployment from API | **Scale out** (workers) | **Decoupled** from checkout like `example2` — **parallel consumers** match spike without inflating the API footprint. |
| **PostgreSQL** (OLTP) | **Primary** CPU, locks, IOPS, connections | Bigger **RDS/Cloud SQL** class, more RAM for cache | **Read replica(s)** for read-heavy paths; (later) sharding for write sharding | **Scale up** primary for Year-1; **add one read replica** for reporting/kitchen if needed | **Single-writer** OLTP: **replicas** help reads; **writes** still **serialize** to one primary. |
| **Object storage + CDN (menu images)** | Egress cost and origin TPS, not RDBMS | Bigger not applicable at app tier — tune **per-object** and lifecycle | **CDN** edge caching, more **prefix parallelism**, multi-region as needed | **Scale out** at the **edge** (CDN) + right-sized buckets | **Bytes** and **geographic** fan-out fit **caching and distribution**, not a bigger API pod. |

**Does not scale infinitely (explicit):** A **single PostgreSQL primary** remains the **authoritative write path** for core orders. You can add replicas and **partition keys** in queries, but **one writer** and **one consistent ordering** of commits mean **unbounded TPS** is not achieved by “more API pods” alone. **Sharding** by key (e.g. `city_id` / tenant) is a **later** cost and **operational** step — not a free default for Year-1.
