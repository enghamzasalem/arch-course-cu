# Part 1.2 — Scale Up vs Scale Out Decision Log

## Decision Table

| Subsystem | Primary Bottleneck | Scale Up Option | Scale Out Option | Year 1 Choice | Rationale |
|---|---|---|---|---|---|
| **Order API pods** | DB connection pool exhaustion; stateless HTTP handlers | Larger pod CPU/RAM limits | Add replicas via HPA (target ~60% CPU); add PgBouncer in front of Postgres | **Scale out** | API pods are stateless — each replica independently handles requests. HPA adds/removes pods in minutes. Vertical pod sizing hits Kubernetes node ceilings quickly and does not survive request bursts. |
| **Notification workers** | External API rate limits; queue depth growth | Larger pod, more goroutines per worker | Increase replica count when queue depth > threshold (KEDA or custom HPA metric) | **Scale out** | Workers are stateless (pull from queue, call external API, ack). More workers drain the queue faster. Rate limit headroom is per-worker so more workers spread the per-worker request rate down. |
| **PostgreSQL primary** | Connection count ceiling; write serialisation; IOPS for active orders | Upgrade to larger RDS/Cloud SQL instance class (more RAM for buffer pool, faster NVME) | Add read replicas for reporting/dashboard queries; logical replication to analytics DB | **Scale up primary + read replicas for reads** | The single-writer OLTP primary cannot be horizontally sharded without application changes (see note below). In Year 1, upgrading instance class gives immediate relief cheaply. Read replicas offload the reporting and dashboard queries that are not latency-sensitive. |
| **Menu image serving** | Egress bandwidth; object store GET rate | Larger egress quota on origin | CDN (CloudFront / Cloudflare) with long TTLs; images served from edge | **Scale out via CDN** | Menu images change infrequently (days to weeks between updates). A CDN cache hit ratio above 90% reduces origin egress by 10x and pushes serving latency from 300 ms (origin) to < 30 ms (edge). No application change required. |
| **Restaurant menu reads (DB)** | Repeated identical queries; high-CPU full table scans | Faster DB instance (more CPU) | Redis cache with `restaurant:{id}:menu` key; TTL 60s; invalidate on menu update | **Cache (scale out read path)** | Caching is the correct mechanism when the same query is repeated identically by many clients (the "duplicate heavy queries per restaurant" pain point). A single Redis node handles hundreds of thousands of GET/s. CPU cost is near-zero compared to a DB query. |

---

## Does Not Scale Infinitely

**PostgreSQL single-writer primary** is the hardest limit in this architecture. A single primary instance can be scaled up to approximately 96 vCPU / 768 GB RAM on current cloud offerings, but write throughput is fundamentally serialised: only one transaction commits at a time to preserve ACID guarantees. At approximately 5,000–10,000 write transactions per second (depending on transaction complexity), even the largest single instance saturates.

Beyond that ceiling, the options are: horizontal application-level sharding (partition `orders` by `city_id` or `restaurant_id` with separate Postgres clusters per shard), or a move to a distributed OLTP database (CockroachDB, YugabyteDB). Both options require significant application changes and operational investment. CityBite should instrument write TPS continuously and plan this migration when the primary consistently exceeds 60% write saturation — well before hitting the ceiling.
