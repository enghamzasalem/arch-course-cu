## Task 3.2

### HPA Rule - Order API

| Parameter | Value | Assumption |
|---|---|---|
| Metric | CPU utilisation | RPS-based would be more precise but requires extra instrumentation |
| Target | 60% average CPU | Leaves headroom before latency degrades |
| Min / max replicas | 2 / 8 | 8 is 4× baseline before DB becomes the binding constraint |

### Backpressure Policy

If queue depth exceeds 5000 events, non-critical endpoints (order history, search) return `503` with `Retry-After: 10`. Checkout remains available - it only writes to the DB and enqueues; it does not depend on the queue being drained.

### Failure Lesson - Scaling Pods but Forgetting the Database

More pods means more DB connections. Postgres fills its connection pool and shared buffers, so query latency climbs even though pod CPU looks healthy, making the root cause non-obvious. Detection requires checking `pg_stat_activity` and p95 DB query latency, not just pod metrics. The fix is PgBouncer (caps server connections regardless of pod count) plus a read replica. Stateless scale-out only moves the bottleneck downstream. Every API scale decision needs a paired DB capacity check.