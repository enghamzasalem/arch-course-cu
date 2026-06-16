# Part 1 — Task 1.2: Scale Up vs Scale Out Decision Log
**CityBite Scalability Architecture | Lecture 10 Assignment**

---

## Decision Table

| # | Subsystem | Primary Bottleneck | Scale Up Option | Scale Out Option | **Year 1 Choice** | Why |
|---|---|---|---|---|---|---|
| 1 | **Order API pods** (Kubernetes Deployment) | CPU saturation and connection-thread exhaustion during dinner spikes | Increase pod CPU/memory requests (`resources.limits`) — fit more goroutines/threads per pod | Add more pod replicas via HPA (`minReplicas: 2 → 10`); spread across nodes | **Scale out (HPA)** | The API is stateless — each pod holds no local state, so replicas are identical and can be added/removed in seconds to track the spike curve; vertical headroom runs out after one or two node sizes and requires a rolling restart |
| 2 | **Notification workers** (SQS consumer Deployment) | SQS queue depth grows faster than workers drain it during peak OPM | Give each worker pod more CPU so it can process messages faster in parallel goroutines | Run more worker pods; KEDA or HPA scales replica count against `ApproximateNumberOfMessagesVisible` | **Scale out (queue-depth autoscaling)** | Notification work is embarrassingly parallel — each message is independent (one SMS/push per order); adding a replica doubles throughput linearly, matching `example2_scalability_queue_workers_citybite.py`'s decoupled worker pattern; scaling up a single pod yields diminishing returns once it is I/O-bound on the external SMS API |
| 3 | **PostgreSQL primary** (managed, e.g. Amazon RDS) | Write IOPS / WAL throughput + connection pool exhaustion; dashboard queries compete with OLTP writes on one instance | Upgrade to a larger RDS instance class (more CPU, more RAM for `shared_buffers`, faster NVMe) | Add read replicas for read traffic; add PgBouncer in front of the primary for connection multiplexing | **Scale up primary + read replicas for reads** | The Postgres **single-writer model is a hard ceiling that does not scale infinitely** — no matter how many application pods exist, all writes funnel through one primary; sharding removes this ceiling but introduces distributed-transaction complexity that is inappropriate for Year 1 order volumes. The pragmatic Year 1 answer is: right-size the primary (scale up once), add one or two read replicas to offload restaurant polling and dashboard queries (selective scale out), and front the primary with PgBouncer to eliminate connection pool exhaustion without adding hardware |
| 4 | **Object storage / CDN** (menu images) | Network egress cost and origin-fetch latency when every menu page load hits the origin | Store images on a faster storage tier (higher-IOPS PVC or premium S3 storage class) | Serve images via a CDN (CloudFront, Cloudflare) with global edge PoPs; origin is hit once per image per region, then cached | **Scale out (CDN edge caching)** | Images are immutable after upload — a CDN hit rate of 95 %+ is realistic, collapsing origin egress to near zero; upgrading the origin storage class reduces the cost of the 5 % cache misses but does not help the 95 % of requests that a CDN removes from the origin entirely |
| 5 | **Redis cache layer** (hot-path menu and session cache) | Cache memory fills as restaurant catalogue grows; eviction causes miss-storm on DB | Upgrade to a larger Redis instance (more RAM, bigger `maxmemory`) | Redis Cluster — partition keyspace across shards; add read replicas per shard | **Scale up (single large instance)** | At Year 1 catalogue size a single Redis instance with generous `maxmemory` (e.g. 16 GB) comfortably holds the full hot menu dataset; the operational overhead of Redis Cluster (cross-slot multi-key commands break, resharding requires care) is not justified until the catalogue grows by an order of magnitude |

---

## "Does Not Scale Infinitely" Note — PostgreSQL Single-Writer Primary

> **The Postgres primary is the one subsystem in this architecture with a hard, non-negotiable write ceiling.**

Every technique described elsewhere in this assignment — HPA for API pods, autoscaled notification workers, Redis caching, read replicas, CDN offload — reduces *read* pressure or *async* workload. None of them changes the fact that every `INSERT INTO orders` and every `UPDATE order_items` must pass through a single primary node that serialises WAL writes.

Concretely:

- A well-tuned `db.r6g.2xlarge` RDS instance can sustain roughly **2 000–4 000 OLTP write transactions per second** before WAL I/O becomes the bottleneck.
- CityBite at Year 1 (one city, dinner rush) is well below this ceiling — scaling up the instance class once is sufficient.
- At Year 3+ (multi-city, millions of orders/day), the write rate will approach the ceiling. The architectural response at that point is **application-level partitioning by city/region** (each city gets its own Postgres cluster), not a single global shard — this matches the `partition key` vocabulary in `example1_scalability_hot_path_citybite.py`.
- **Operational cost of shards:** each shard requires its own backup schedule, failover configuration, monitoring, and schema migration pipeline. Introducing sharding prematurely adds months of engineering overhead for a problem that does not yet exist. The "does not scale infinitely" acknowledgement is therefore also a deliberate *deferral decision*: document the ceiling, instrument the approach metric (WAL write rate), and trigger the sharding project when the metric hits 60 % of the ceiling — not before.

---

## Decision Summary

```
Stateless compute (API pods, workers) ── Scale OUT  ── HPA / queue-depth autoscaling
Stateful primary DB (Postgres)         ── Scale UP   ── then read replicas; shard deferred
Cache layer (Redis)                    ── Scale UP   ── cluster deferred to Year 2+
Binary assets (images)                 ── Scale OUT  ── CDN edge; origin tier unchanged
```

The pattern is consistent with lecture guidance: **scale out what is stateless; scale up what holds shared mutable state until the cost of distribution is justified by the workload.**

---

*Terminology aligned with `example1_scalability_hot_path_citybite.py` (hot path, partition key) and `example2_scalability_queue_workers_citybite.py` (decoupled worker scaling).*
