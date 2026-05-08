## Task 2.1

### Liveness vs Readiness - Order API

**Liveness** probe hits `/healthz` (shallow: confirms the process is running and not deadlocked). If it fails, Kubernetes restarts the pod. It proves the process is alive, not that it can serve traffic.

**Readiness** probe hits `/readyz` (deep: opens a DB connection and asserts it succeeds). If it fails, Kubernetes removes the pod from the load balancer without restarting it. It proves the pod can actually handle requests.

### Why `/healthz` 200 OK Can Lie`

`example2` distinguishes a shallow health check (process responds) from a deep one (dependencies reachable). A pod under DB connection-pool exhaustion will return `200 OK` on `/healthz` because the process is alive, but every real request will fail or queue indefinitely. This is the "green pods that cannot reach DB" pain point from the baseline. The readiness probe on `/readyz` catches this by actually acquiring a connection. If the pool is exhausted, `/readyz` fails and the pod is pulled from the load balancer before users see errors.

### Synthetic Check

Every 60 seconds, an external probe submits a test checkout against a dedicated staging restaurant and asserts: HTTP 200 received within 3 seconds, response body contains a valid `order_id`. This catches failures that only appear from the outside, for example, if the domain stops resolving, the certificate expires, or the payment provider goes down, none of which an internal pod would notice about itself.

### Alerting

**Alert 1 - Checkout error rate**
Threshold: >1% of checkout requests return non-2xx over a 5-minute window.
Runbook first step: check payment gateway status page; if healthy, check for connection exhaustion.

**Alert 2 - Readiness probe failure rate**
Threshold: >25% of Order API pods failing `/readyz` for more than 2 minutes.
Runbook first step: check how many open database connections there are and whether the database server is under heavy load; if both are high, limit how many new connections the API is allowed to open and wake the database on-call person.