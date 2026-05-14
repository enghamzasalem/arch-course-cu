# Part 2.1 — Monitoring & Probes

## 1. Liveness vs Readiness for the Order API

### Liveness Probe

| Attribute | Detail |
|-----------|--------|
| Path | `GET /livez` |
| What it proves | The Python/Node process is alive and its event loop (or thread pool) is not deadlocked. The handler does nothing except return `HTTP 200 {"status": "alive"}`. |
| Failure action | Kubernetes **restarts the container**. A liveness failure means the process is unrecoverable in its current state — a restart is the correct remedy. |
| Timing | `initialDelaySeconds: 10`, `periodSeconds: 10`, `failureThreshold: 3` |

### Readiness Probe

| Attribute | Detail |
|-----------|--------|
| Path | `GET /readyz` |
| What it proves | The pod can actually serve traffic right now. The handler attempts to acquire a connection from the DB pool (with a short timeout, e.g. 50 ms) and checks that the internal job queue consumer is running. Returns `HTTP 200` only if both checks pass. |
| Failure action | Kubernetes **removes the pod from the Service's endpoint list** (load balancer stops sending traffic). The pod is not restarted — it stays running but receives no new requests until it recovers. |
| Timing | `initialDelaySeconds: 5`, `periodSeconds: 5`, `failureThreshold: 2` |

The key distinction: liveness answers "is the process alive?"; readiness answers "is the process useful right now?". A pod can be live but not ready (e.g. DB pool exhausted), and Kubernetes must handle each case differently.

---

## 2. Contrast with `example2` — Why `/healthz` Can Lie

`example2_availability_monitoring_citybite.py` demonstrates exactly this failure mode. The `shallow_health()` function always returns `True` because it only checks whether the Python process responded — it does not touch any dependency. Meanwhile, `deep_readiness(pool)` tries to acquire a DB connection and returns `False` when the pool is exhausted.

In the simulation, all pool slots are held by stuck request handlers. The shallow probe reports the pod as healthy, so the load balancer keeps routing new checkout requests to it. Those requests immediately queue behind the stuck handlers, exhaust the remaining thread budget, and the pod becomes completely unresponsive — yet Kubernetes never removes it from rotation because `/healthz` keeps returning 200.

This is **pool exhaustion masquerading as health**. The fix is exactly what the readiness probe above implements: the `/readyz` handler must perform a cheap but real dependency check (try-acquire + immediate release) so that a pod that cannot reach the DB is removed from the load balancer before it accumulates more stuck requests.

---

## 3. Synthetic Check (Black-Box Probe)

**What:** A synthetic monitor runs from **outside the cluster** (e.g. a managed uptime service like Checkly, Datadog Synthetics, or a simple Lambda on a cron) every 60 seconds. It performs a full end-to-end checkout against a dedicated test restaurant and test payment token:

1. `POST /orders` with a known test payload and Stripe test card `4242 4242 4242 4242`.
2. Assert: HTTP 201 returned within 3 seconds.
3. Assert: response body contains `order_id` and `status: "confirmed"`.
4. `GET /orders/{order_id}` — assert the order is retrievable and status matches.

**Why this matters:** The synthetic check exercises the real network path (DNS, TLS, load balancer, API, DB, payment gateway sandbox) from the customer's perspective. It catches issues that internal probes miss: a misconfigured ingress, an expired TLS certificate, a broken payment gateway integration, or a DNS propagation failure after a deployment. It is the closest approximation to "can a real customer place an order right now?"

---

## 4. Alerting

### Alert 1: High Checkout Failure Rate

| Attribute | Detail |
|-----------|--------|
| Metric | `checkout_success_rate` (5-minute rolling window) |
| Threshold | Rate drops below **98%** for 5 consecutive minutes |
| Severity | P1 — page on-call engineer immediately |
| Runbook first step | Check the circuit breaker state dashboard. If the payment gateway breaker is OPEN, the gateway is the likely cause — check the gateway's status page and Slack channel. If the breaker is CLOSED, check Order API error logs for DB connection errors or application exceptions. |

### Alert 2: DB Connection Pool Near Exhaustion

| Attribute | Detail |
|-----------|--------|
| Metric | `db_pool_connections_in_use / db_pool_max_connections` |
| Threshold | Ratio exceeds **85%** for 3 consecutive minutes |
| Severity | P2 — notify on-call engineer (no immediate page) |
| Runbook first step | Identify which endpoint is holding connections longest using `pg_stat_activity`. Check for long-running transactions or missing `finally` blocks that fail to release connections. If the ratio is still climbing, scale the Order API deployment horizontally to distribute pool pressure, and consider reducing `max_connections` per pod to prevent a single pod from monopolising the DB. |
