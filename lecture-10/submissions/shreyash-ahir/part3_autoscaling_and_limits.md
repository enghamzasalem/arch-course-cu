# Part 3.2 — Autoscaling and Backpressure

## HPA Rule: Order API

```yaml
# Assumptions: labeled as such
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-api
  minReplicas: 3          # ASSUMPTION: 3 pods handle steady-state (~80 RPS total)
  maxReplicas: 20         # ASSUMPTION: 20 pods * ~30 RPS/pod capacity = ~600 RPS peak
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60   # ASSUMPTION: scale out before saturation at 80%+
```

**Metric rationale:** CPU utilization is the most reliable signal for the Order API because
request processing is CPU-bound (JWT validation, JSON serialization, DB query wait).
An alternative metric is requests-per-second via KEDA + Prometheus, which reacts faster
to traffic spikes before CPU rises, but requires additional instrumentation. For Year 1,
CPU at 60% target is a safe conservative threshold.

**Scaling behavior:** HPA checks every 15 seconds. With `--horizontal-pod-autoscaler-upscale-delay=0` and a stabilization window of 60 seconds for scale-down (to avoid flapping), pods are added within 30–60 seconds of a traffic spike, which is fast enough for the 2-hour dinner rush pattern.

---

## Backpressure / Degradation Policy

**Scenario: SQS notification queue depth exceeds 10,000 messages**

This indicates that notification workers cannot drain the queue fast enough (e.g.
external SMS provider is rate-limiting). Policy:

1. **Scale out workers first:** KEDA scales notification worker replicas from 3 to up to
   15 based on `ApproximateNumberOfMessagesVisible > 500`.

2. **Shed non-critical notifications:** If queue depth exceeds 10,000, the worker
   switches to processing only `type=order_confirmation` messages (skip promotional
   push notifications). Low-priority messages are re-queued to a dead-letter queue for
   later reprocessing.

3. **503 with Retry-After for order endpoints if DB pool is exhausted:** If
   PgBouncer reports `cl_waiting > 50` (50 clients waiting for a connection), the
   Order API returns `503 Service Unavailable` with `Retry-After: 5` instead of
   queuing indefinitely. This prevents cascading timeouts and gives the mobile app
   a clear signal to retry rather than show a spinner for 30 seconds.

---

## Failure Lesson: Scaling Pods Without Scaling the Database

**Symptoms:**

You scale the Order API from 3 to 15 pods in response to a dinner rush. Response times
drop briefly, then get worse than before. The Kubernetes dashboard shows CPU on API
pods at 40% (plenty of headroom), but p95 latency climbs from 200 ms to 4 seconds.
Error logs fill with `ERROR: remaining connection slots are reserved for replication`.

**What is actually happening:**

Each additional API pod opens its own PgBouncer transaction pool. 15 pods times 10
connections per pod pool equals 150 active connections. PostgreSQL's `max_connections`
is set to 100 (a common default). The excess connection requests queue inside
PgBouncer and then time out. The database CPU is at 95% because every query waits
longer, holding its connection open longer, amplifying the connection shortage.

**Detection:**

The signal is visible in two places that are often not on the primary dashboard: (1)
`pg_stat_activity` showing 90+ connections in `idle in transaction` state; (2) PgBouncer
`cl_waiting` counter increasing monotonically. CPU and memory on API pods look healthy
— this is the misleading indicator that causes operators to add more pods, making the
problem worse.

**Mitigation:**

First, reduce the per-pod connection pool size in PgBouncer config (5 connections per
pod rather than 10, so 15 pods use 75 connections total). Second, increase
`max_connections` on Postgres to 200 and allocate corresponding `shared_buffers`.
Third, add the Postgres primary to the HPA alert dashboard so that DB connection
saturation is visible alongside pod CPU. In the medium term, introduce a dedicated
PgBouncer instance in `transaction` pooling mode in front of Postgres — this allows
hundreds of application connections to share a small number of true Postgres server
connections, breaking the coupling between pod count and DB connection count entirely.
