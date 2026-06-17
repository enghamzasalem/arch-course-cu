# Part 1.1 – Workload Dimensions and Bottlenecks

## Five Workload Dimensions

| Workload Dimension | Primary Saturation Resource | Why It Matters |
|--------------------|----------------------------|----------------|
| Concurrent customers | DB connections | Dinner rush spikes connection pool |
| Orders per minute | CPU (API + DB write) | Peak hour orders overwhelm hot path |
| Restaurants onboarded | Disk IOPS (menu images) | More restaurants = more images stored/retrieved |
| Menu image bytes | Network egress + S3 bandwidth | Each order reads multiple menu images |
| Dispatch dashboard queries | DB read replica CPU | Restaurant tablets refresh frequently |

## Hero Scenario: Friday 19:00–21:00 (One City)

**If scaled well:** Users see orders confirmed within 2 seconds. Restaurant tablets show new orders instantly. No timeouts. Dispatch dashboard updates smoothly.

**If scaled poorly:** Users see loading spinners. Orders take 10+ seconds. Restaurants miss orders. DB connection pool exhausted. Some users get 503 errors.

**Key metric to watch:** p95 order confirmation latency.

## Summary

The critical bottleneck is the **PostgreSQL primary** during write-heavy peak hours. Mitigations include read replicas for queries, connection pooling (PGBouncer), and offloading notifications to async queue.