# Part 3 — Task 3.2: Autoscaling and Backpressure
**CityBite Scalability Architecture | Lecture 10 Assignment**

---

## 3.2.1 HPA Rule — Order API

### Rule specification

```yaml
# ASSUMPTIONS are labelled inline
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-api-hpa
  namespace: citybite
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-api
  minReplicas: 2        # ASSUMPTION: 2 pods handles steady off-peak load (~50 req/s)
  maxReplicas: 16       # ASSUMPTION: 16 pods is the ceiling before PgBouncer/DB becomes
                        # the binding constraint; adding more pods beyond this
                        # produces no throughput gain and wastes node capacity
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60   # ASSUMPTION: 60% CPU triggers scale-out;
                                   # chosen to leave headroom for a sudden spike
                                   # before the next pod is ready (~30 s startup)
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30   # ASSUMPTION: fast scale-up for dinner ramp
      policies:
        - type: Pods
          value: 4                     # add up to 4 pods per scale event
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300  # ASSUMPTION: slow scale-down to avoid
                                       # thrashing at the tail of the dinner window
```

### Why CPU at 60%?

CPU utilisation is the most practical signal available without a custom metrics pipeline. Each Order API request is CPU-bound during cart validation, JWT verification, and JSON serialisation; CPU therefore tracks request rate closely. A target of 60% (rather than the Kubernetes default of 80%) preserves a 20-percentage-point buffer for the ~30-second pod startup latency — if a spike arrives and the scaler fires at 60%, new pods are ready before utilisation reaches saturation at ~95%. 

At Year 2, replacing CPU with a custom RPS-per-pod metric (sourced from the Ingress NGINX Prometheus exporter) would be more precise because CPU can be misleading when some requests are I/O-bound waiting on the database, but this requires a Prometheus adapter in the cluster, which is deferred to Year 2.

### Capacity assumptions (labelled)

| Assumption | Value | Basis |
|---|---|---|
| Steady-state request rate | ~50 req/s | ASSUMPTION — single city, off-peak |
| Peak request rate | ~500 req/s | ASSUMPTION — 10× multiplier from Task 1.3 hero scenario |
| Per-pod throughput at 60% CPU | ~35–40 req/s | ASSUMPTION — based on typical Go/Node API benchmarks at 0.5 CPU request |
| Pods needed at peak | ~13–15 | ASSUMPTION — 500 / 37 ≈ 13.5, rounds to 14; `maxReplicas: 16` gives margin |
| Pod startup time | ~30 s | ASSUMPTION — includes readiness probe warm-up |

---

## 3.2.2 Backpressure and Degradation Policy

### Scenario: SQS notification queue depth exceeds threshold

During a marketing spike, the notification worker pool may fall behind even after KEDA autoscaling fires. If the SQS `ApproximateNumberOfMessagesVisible` depth exceeds **10 000 messages** (ASSUMPTION: roughly 5 minutes of peak order volume at 2 000 OPM), the system applies a tiered degradation policy rather than failing the entire checkout flow.

#### Tier 1 — Shed non-critical notification channels (queue depth > 10 000)

The notification worker applies a **feature flag check** before processing each message. When the queue depth signal is above threshold, the worker skips low-priority channels (marketing upsell SMS, loyalty point notifications) and processes only the order-confirmation push notification and the restaurant alert. This halves the per-message processing time without any customer-visible checkout failure.

#### Tier 2 — Drop analytics events, retain order-critical events (queue depth > 25 000)

If depth continues to rise, the outbox poller stops emitting analytics events to the queue entirely — analytics ingestion is explicitly eventually consistent and can replay from the outbox table once the spike clears. Order-confirmation and dispatch events continue unaffected.

#### Tier 3 — 503 with `Retry-After` at the API (queue depth > 50 000 or DB connection pool exhausted)

If the queue depth signal indicates the system is genuinely overwhelmed, or if PgBouncer reports connection pool exhaustion, the Order API returns:

```http
HTTP/1.1 503 Service Unavailable
Retry-After: 30
Content-Type: application/json

{
  "error": "service_busy",
  "message": "CityBite is experiencing high demand. Please try again shortly.",
  "retry_after_seconds": 30
}
```

The `Retry-After: 30` header is critical: it signals compliant clients (and the mobile app) to back off for 30 seconds, which converts a thundering-herd retry storm into a smooth ramp-down. Without it, every client that receives a 503 immediately retries, amplifying the load that caused the 503 in the first place.

#### Why not just drop requests silently?

Silent dropping (TCP reset or no response) causes mobile clients to retry immediately and aggressively, worsening the overload. A well-formed 503 with `Retry-After` is the correct backpressure signal that co-operates with client retry logic to let the system recover.

---

## 3.2.3 Failure Lesson — Scaling Pods but Forgetting the Database

### What happens

Suppose the CityBite team correctly configures HPA and watches the Order API pod count climb from 2 to 16 during Friday dinner rush. Requests per second handled by the API tier doubles, then quadruples — the Ingress metrics look healthy, pod CPU is under control, and the engineering team feels confident. Then, at approximately 19:35, Postgres begins to exhibit symptoms: query latency climbs from 5 ms to 200 ms, then to 2 000 ms, as 16 pods × 10 connections each = 160 concurrent connections hammer the primary simultaneously, exhausting both the connection limit and the WAL write buffer. Connection pool wait time inside PgBouncer spikes, and the Order API's database calls start timing out — but because the pods themselves are healthy, HPA does not scale down, and the Ingress keeps routing new requests to pods that are now stuck waiting for a database connection that will never arrive. From the customer's perspective, the checkout spinner runs indefinitely; from the restaurant tablet's perspective, new orders stop appearing; from the ops team's perspective, the pod metrics look fine while the database metrics are screaming — and the two dashboards may not even be on the same screen.

### Symptoms

- p95 and p99 API latency climbs steeply while pod CPU remains low (the pods are idle, waiting on DB I/O)
- Postgres `max_connections` alert fires; `pg_stat_activity` shows hundreds of idle-in-transaction connections
- PgBouncer `cl_waiting` metric (clients waiting for a server connection) grows without bound
- Application error logs fill with `connection timeout` and `deadlock detected` errors
- SQS queue depth grows because workers also share the DB connection pool

### Detection

The key observability gap is **treating pod CPU as a proxy for system health**. The correct alert stack is:

| Metric | Tool | Alert threshold |
|---|---|---|
| Postgres `pg_stat_activity` connection count | CloudWatch / Prometheus | > 80% of `max_connections` |
| PgBouncer `cl_waiting` | Prometheus exporter | > 10 waiting clients for > 30 s |
| API p95 latency | Ingress metrics | > 500 ms for > 60 s |
| Postgres WAL write rate | RDS CloudWatch | > 60% of instance I/O capacity |

### Mitigation

The immediate mitigation is to **cap `maxReplicas` at a value that keeps total DB connections below PgBouncer's server pool size** — in the YAML above, `maxReplicas: 16` at 10 connections per pod = 160 client connections, which PgBouncer multiplexes onto a server pool of 20–30 actual Postgres connections. This means the database sees at most 30 concurrent connections regardless of how many pods are running, decoupling pod autoscaling from database connection pressure. The lesson is that **every autoscaling ceiling must be derived from the capacity of the most constrained downstream dependency**, not from the capacity of the component being scaled.

---

## Final Overview

| Concern | Mechanism | Key number |
|---|---|---|
| Order API scale-out | HPA on CPU 60% | min 2 / max 16 pods |
| Notification overload | Tiered feature shedding + 503 Retry-After | Queue depth thresholds: 10k / 25k / 50k |
| DB connection ceiling | PgBouncer server pool cap | 20–30 Postgres connections regardless of pod count |
| Forgetting the DB | Alert on pg_stat_activity + PgBouncer cl_waiting | Fire before max_connections is reached |

---

*Terminology aligned with `example2_scalability_queue_workers_citybite.py` (worker autoscaling, queue depth as backpressure signal) and Task 1.2 scale decisions (PgBouncer, maxReplicas ceiling).*
