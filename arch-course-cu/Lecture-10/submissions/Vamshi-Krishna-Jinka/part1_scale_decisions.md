# Part 1: Workload Model and Bottlenecks
## Task 1.2: Scale Up vs Scale Out Decision Log

## 1. Overview
This decision log explains where CityBite should use vertical scaling (scale up) and where it should use horizontal scaling (scale out). The goal is to match the scaling method to the subsystem bottleneck instead of adding more servers everywhere.

---

## 2. Scale Up vs Scale Out Decisions

| Subsystem | Primary bottleneck | Scale up option | Scale out option | Year 1 choice | Why |
|---|---|---|---|---|---|
| Order API pods | CPU and memory during traffic spikes | Bigger pod size, more CPU/RAM per pod | More replicas behind the service | Scale out | Multiple API pods handle dinner rush better and reduce the risk of one busy pod becoming a bottleneck. |
| Notification workers | Outbound I/O and queue drain speed | Faster worker instances with more CPU | More worker replicas consuming the queue | Scale out | Notifications are independent jobs, so more workers can drain the queue in parallel during peak hours. |
| PostgreSQL primary | DB connections, CPU, and write throughput | Larger DB instance with more CPU/RAM and IOPS | Read replicas for read-heavy traffic; partitioning for some tables | Scale up first, then optimize reads | The primary database is still the write bottleneck, so a stronger single instance is the simplest first step. |
| Object storage / CDN | Network egress and media delivery latency | Larger storage node or faster network | Multiple edge nodes / CDN caching | Scale out | Images should be served from cached edge locations so menu browsing stays fast across many users. |
| Dispatch dashboard API | Read-heavy queries and repeated restaurant lookups | Larger app server and cache size | More dashboard replicas and cached reads | Scale out | Dashboard traffic can be spread across replicas, especially when heavy queries are cached. |

---

## 3. Important Limit Note

### Does not scale infinitely
PostgreSQL as a single-writer OLTP primary does not scale infinitely. Even with a larger instance, write throughput, connection limits, and lock contention eventually become a ceiling. For that reason, Year 1 should also include read replicas, caching, and query reduction so the primary is protected.

---

## 4. Summary
For CityBite, scale out is usually better for stateless services such as the API and workers. Scale up is useful for the database at first, but it has a clear limit. The best design is to scale each subsystem according to how it fails, not by using one scaling strategy for everything.
