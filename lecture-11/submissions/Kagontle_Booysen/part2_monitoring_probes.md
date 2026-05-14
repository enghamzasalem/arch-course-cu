# Part 2 — Task 2.1: Monitoring & Probes
**Assignment:** Software Architecture — Lecture 11 (Availability and Services)  
**Product:** CityBite  
**Component:** Order API (K8s Deployment)

---

## 2.1.1 Liveness vs Readiness for the Order API

Kubernetes exposes two independent probe mechanisms that answer fundamentally different questions. They must be configured separately because conflating them is one of the most common causes of self-inflicted availability incidents.

### Liveness Probe — "Is this process worth keeping alive?"

| Attribute | Value |
|-----------|-------|
| Path | `GET /internal/livez` |
| Port | 8080 (internal, not exposed via Ingress) |
| Initial delay | 15 s (allow JVM/Python runtime to start) |
| Period | 10 s |
| Failure threshold | 3 consecutive failures → kubelet restarts the pod |
| Success threshold | 1 |
| Timeout | 2 s |

**What it proves:** The HTTP server process is running and its event loop is not deadlocked. The `/internal/livez` handler does the minimum possible work: it returns `{"status": "alive"}` with HTTP 200. It checks nothing external. It does not query Postgres. It does not call the payment gateway. It does not check queue depth.

**Failure action:** If the liveness probe fails three times consecutively, kubelet **kills and restarts the pod**. This is a last-resort recovery mechanism — it handles the case where the Order API process has entered a deadlock, an infinite loop, or an OOM state from which it cannot self-recover. Because the liveness probe touches nothing external, a false positive (e.g., Postgres is down) will never cause a pod restart storm.

```yaml
livenessProbe:
  httpGet:
    path: /internal/livez
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
  timeoutSeconds: 2
```

---

### Readiness Probe — "Is this pod safe to receive customer traffic?"

| Attribute | Value |
|-----------|-------|
| Path | `GET /internal/readyz` |
| Port | 8080 (internal) |
| Initial delay | 5 s |
| Period | 5 s |
| Failure threshold | 2 consecutive failures → pod removed from Service Endpoints |
| Success threshold | 2 consecutive successes → pod re-added |
| Timeout | 3 s |

**What it proves:** The pod can successfully complete the critical path it is about to serve. The `/internal/readyz` handler performs the following checks in order:

1. **DB connectivity check** — executes `SELECT 1` against the Postgres connection pool. A result within 500 ms is a pass; a timeout or pool-exhaustion error is a fail.
2. **Connection pool headroom check** — verifies that fewer than 80 % of the pool's `max_connections` are in use. If the pool is at 95 % capacity, the pod returns HTTP 503 even if individual queries succeed, because accepting more traffic would push the pool to exhaustion within seconds.
3. **Downstream dependency check (shallow)** — performs a HEAD request to the payment gateway's `/health` endpoint with a 1 s timeout. A non-2xx or timeout is recorded but **does not fail the readiness probe** — instead it sets a flag that activates the circuit breaker (see Task 2.2). This avoids a situation where a payment gateway outage marks all Order API pods unready and takes down the entire service.

**Failure action:** If the readiness probe fails twice consecutively, the pod's IP is **removed from the Kubernetes Service's Endpoints list**. The load balancer stops routing new requests to it. The pod is not restarted. If and when the underlying condition resolves (DB recovers, pool drains), the pod passes two consecutive readiness checks and is silently re-added to the endpoint pool. This is a graceful, reversible operation — the opposite of the liveness restart.

```yaml
readinessProbe:
  httpGet:
    path: /internal/readyz
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 2
  successThreshold: 2
  timeoutSeconds: 3
```

### Summary: what each probe owns

| | Liveness `/internal/livez` | Readiness `/internal/readyz` |
|--|---------------------------|------------------------------|
| Checks process? | ✅ Yes | ✅ Yes (implicit — handler runs) |
| Checks DB? | ❌ Never | ✅ Yes (`SELECT 1` + pool headroom) |
| Checks external services? | ❌ Never | ⚠️ Shallow only (no fail-on-error) |
| Failure action | Pod **restart** | Pod **removed from LB** |
| False positive risk | Very low | Medium — requires careful threshold tuning |
| Recovery | Automatic (restart) | Automatic (re-added on success) |

---

## 2.1.2 Why "200 OK on `/healthz`" Can Lie Under Pool Exhaustion

`example2_availability_monitoring_citybite.py` demonstrates a shallow health endpoint that returns HTTP 200 as long as the process is alive. This is the most common health-check anti-pattern, and it creates a specific failure mode that is difficult to diagnose in production.

### The failure sequence

Consider the following scenario on a Friday evening peak:

1. Order API has 10 pods. Each pod has a Postgres connection pool of 20 connections (`max_connections = 20`).
2. A slow upstream dependency (the payment gateway, responding in 4 s instead of 400 ms) causes checkout requests to hold their DB connections open for longer, waiting for the payment result before committing the order row.
3. Within 2 minutes, all 20 connections in every pod's pool are occupied. New checkout requests arrive, call `pool.acquire()`, and block.
4. The `/healthz` handler in `example2` does this:

```python
# example2_availability_monitoring_citybite.py — shallow check
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}   # Returns 200 regardless of pool state
```

5. Kubernetes polls `/healthz` every 10 seconds. It gets HTTP 200 in < 1 ms because the handler never touches the pool. **All 10 pods remain in the Endpoints list.**
6. The load balancer continues routing customer traffic to all 10 pods. Every checkout request blocks indefinitely on `pool.acquire()`. The Order API is functionally down — but Kubernetes has no idea.
7. Customers see spinning loaders. Support tickets spike. The on-call engineer checks the Kubernetes dashboard: **all pods green**.

This is the "green pods that cannot reach DB" failure described in the assignment baseline. The shallow `/healthz` lies because it proves only that the Python process and its HTTP server are alive. It proves nothing about the pod's ability to execute any real work.

### What the deep readiness probe catches instead

The `/internal/readyz` handler described in Section 2.1.1 checks `pool.get_checked_out_connections() / pool.max_connections`. At 80 % pool utilisation, it returns HTTP 503. Kubernetes removes that pod from the load balancer. Traffic is redistributed to pods that still have headroom. This does not fix the root cause (the slow gateway), but it prevents healthy pods from being overwhelmed by traffic redirected from the degraded ones, and it gives the circuit breaker time to open and shed load from the gateway path entirely.

The key insight: **a health check that cannot fail under the conditions that actually cause outages is not a health check — it is a false signal that delays detection and increases blast radius.**

---

## 2.1.3 Synthetic Black-Box Probe (External Check)

Internal Kubernetes probes observe pod health from inside the cluster. They cannot detect failures in the network path between the customer and the cluster: DNS resolution failures, TLS certificate expiry, CDN misconfiguration, Ingress controller bugs, or load balancer rule errors. A synthetic black-box probe runs from **outside the cluster**, from a vantage point that approximates what a real customer experiences.

### Probe definition: End-to-End Checkout Canary

| Attribute | Value |
|-----------|-------|
| Type | HTTPS synthetic transaction |
| Operator | Managed uptime service (e.g., Checkly, Datadog Synthetics) running from two geographic regions (Frankfurt + London) |
| Schedule | Every 60 seconds |
| Credentials | Dedicated `canary_user` account with a pre-funded test wallet; uses a Stripe test card (`4242 4242 4242 4242`) connected to a sandbox payment environment |

**What the probe asserts, in order:**

1. `POST https://api.citybite.com/v1/orders` with a valid canary order payload resolves DNS successfully and the TLS handshake completes with a valid, non-expired certificate.
2. The response is HTTP 201 (Created), not a redirect or error page.
3. The response body contains `"status": "CONFIRMED"` and a non-null `order_id`.
4. The full round-trip completes within **2 500 ms** (500 ms headroom below the SLI threshold of 3 000 ms — the probe should alert *before* the SLO starts burning).
5. The response `Content-Type` header is `application/json` (guards against Ingress returning an HTML error page with HTTP 200 — another common "lying health check" pattern).

**On assertion failure:** The probe fires an alert within 2 consecutive failures (120 s) to avoid noise from single transient network blips. The canary order is automatically cancelled via a cleanup call to `/v1/orders/{order_id}/cancel` regardless of assertion outcome, so it does not pollute the production order database.

**Why two regions?** A single-region probe cannot distinguish between a global outage and a regional network issue at the probe's vantage point. If Frankfurt fails but London succeeds, the incident is likely a routing or DNS issue between Frankfurt and the CityBite edge, not a full service outage. This context is critical for the on-call runbook's first step.

---

## 2.1.4 Alerting — Two Alerts with Thresholds and Runbook First Steps

---

### Alert 1 — Checkout SLI Burn Rate Critical

**Purpose:** Detect when the error budget (defined in Task 1.2) is burning fast enough to exhaust the 30-day budget within 1 hour if unchecked — the most urgent class of availability signal.

**Prometheus alert rule:**

```yaml
- alert: CheckoutSLIBurnRateCritical
  expr: |
    (
      rate(citybite_checkout_requests_total{result="bad"}[5m])
      / rate(citybite_checkout_requests_total{result="valid"}[5m])
    ) > 0.05
  for: 2m
  labels:
    severity: page
    journey: place_paid_order
  annotations:
    summary: "Checkout SLI burn rate critical — error rate > 5 % for 2 min"
    description: >
      The bad-event rate on POST /v1/orders has exceeded 5 % of valid requests
      for 2 consecutive minutes. At this rate, the 30-day error budget will be
      exhausted in under 72 hours. Current rate: {{ $value | humanizePercentage }}.
```

**Threshold justification:** 5 % error rate represents a 10× burn rate against the 0.5 % monthly failure allowance. At 10× burn, the entire monthly budget expires in 3 days. The `for: 2m` guard filters transient single-minute spikes that self-resolve, while still alerting fast enough for an on-call response to matter.

**Runbook first step:**
> Open the Grafana **Checkout Journey** dashboard. Check the panel `citybite_checkout_requests_total` broken down by `result` and `pod`. Determine within 60 seconds: (a) is the error rate uniform across all pods, or isolated to a subset? If isolated → suspect a bad deploy; check the rollout history with `kubectl rollout history deployment/order-api`. If uniform → suspect an external dependency; check the Payment Gateway circuit breaker state in the `citybite_circuit_breaker_state` metric. If the circuit is OPEN, confirm the fallback processor is active before escalating.

---

### Alert 2 — Order API Readiness Pool Exhaustion Warning

**Purpose:** Detect Postgres connection pool pressure *before* pods start failing readiness checks and being removed from the load balancer — catching the condition described in Section 2.1.2 while there is still capacity headroom to act.

**Prometheus alert rule:**

```yaml
- alert: OrderAPIPoolExhaustionWarning
  expr: |
    citybite_db_pool_checked_out_connections
    / citybite_db_pool_max_connections
    > 0.70
  for: 3m
  labels:
    severity: warn
    component: order-api
  annotations:
    summary: "DB connection pool > 70 % utilised for 3 min on {{ $labels.pod }}"
    description: >
      Pod {{ $labels.pod }} has used more than 70 % of its Postgres connection pool
      for 3 consecutive minutes. At 80 %, the readiness probe will begin returning
      503 and the pod will be removed from the load balancer. Remaining headroom:
      {{ $value | humanizePercentage }} utilised.
```

**Threshold justification:** The readiness probe fails at 80 % pool utilisation. This alert fires at 70 %, giving the on-call engineer a ~3–5 minute intervention window before customer-visible impact begins. The `for: 3m` guard avoids alerting on legitimate short-duration traffic bursts (e.g., a flash sale starting) that the pool can absorb and drain naturally.

**Runbook first step:**
> SSH into the Grafana dashboard and check `citybite_checkout_request_duration_p99` for the affected pod. If p99 latency has increased above 2 000 ms in the same window, the pool pressure is likely caused by slow downstream calls holding connections open — check the payment gateway latency metric `citybite_payment_gateway_duration_ms`. If the gateway p99 is above 1 500 ms, manually trigger the circuit breaker open via the Order API admin endpoint: `POST /internal/admin/circuit-breaker/payment/open` (requires on-call token). If gateway latency is normal, check for a slow query using `pg_stat_activity` on the Postgres replica; look for long-running transactions blocking row locks.

---

## Overview of each components 

| Mechanism | Scope | What it catches | Action |
|-----------|-------|----------------|--------|
| Liveness probe `/internal/livez` | In-cluster, per-pod | Deadlock, OOM, process crash | Pod restart |
| Readiness probe `/internal/readyz` | In-cluster, per-pod | DB pool exhaustion, slow pool, connectivity loss | Remove pod from LB |
| Synthetic black-box probe | External, end-to-end | DNS failure, TLS expiry, Ingress misconfiguration, full path breakage | PagerDuty alert |
| Alert 1: SLI burn rate | Cluster-wide, journey-level | Elevated checkout failures or latency | Page on-call |
| Alert 2: Pool exhaustion | Per-pod | DB connection pressure before readiness failure | Warn on-call |

The five mechanisms form overlapping layers: no single failure mode can go undetected, and no single probe can trigger a false alarm that takes down the service on its own.

---

*Continues in Task 2.2: Cascading failure controls — circuit breaker, timeouts, and bulkhead.*
