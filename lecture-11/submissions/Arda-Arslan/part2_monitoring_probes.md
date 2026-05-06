# Task 2.1 - Monitoring and Probes

## Liveness vs readiness for the Order API

**Liveness probe**: path `/livez`. The pod answers OK if the Python process is running and not stuck. It does not check the database or any external service. If liveness fails for a few seconds in a row, Kubernetes restarts the pod. The point is to recover from things like deadlocks or hung threads where the process is alive but cannot do anything.

**Readiness probe**: path `/readyz`. The pod answers OK only if it can actually serve a request: it checks that it can get a connection from the database pool and that startup is finished. If readiness fails, Kubernetes removes the pod from the load balancer but does not restart it. As soon as readiness comes back, the pod gets traffic again.

The split matters because the two failures need different actions. A stuck process needs a restart. A pod that cannot reach the DB right now should not get traffic, but restarting it will not fix the DB and would only make things worse during a rollout.

## Why "200 OK on /healthz" can lie

In `example2_availability_monitoring_citybite.py`, the shallow `health()` function returns True just because the Python process is alive. It does not look at the DB pool. The deep `readiness()` function tries to acquire a real pool slot, and when the pool is full it returns False.

This is exactly the trap on a real pod. If readiness only returns 200 because the HTTP handler can run, the load balancer keeps sending checkouts to a pod whose DB pool is exhausted. From outside everything looks green, but customers see timeouts. Readiness has to check the dependencies that the pod actually needs to take an order, not just that the process is up.

## Synthetic check from outside the cluster

We run one synthetic check from an external monitoring service (different region from the cluster, no shared network). Every minute it makes a real HTTPS request to the public API: a small "menu fetch + create test order" flow with a test account and a test payment method.

It asserts:
- HTTP 200 within 3 seconds.
- The response contains an order id.
- The order ends up in the "confirmed and paid" state when checked one minute later.

This is closer to what a real customer experiences than any internal probe, because it goes through DNS, TLS, ingress, the API, the DB, and the payment gateway sandbox. If the cluster is fine but DNS is broken, internal probes will not catch it but this one will.

## Alerts

**Alert 1 - Checkout success rate dropping (user-visible)**
- Threshold: successful checkout ratio drops below 99% over the last 15 minutes.
- Severity: page the on-call engineer.
- Runbook first step: open the checkout dashboard and split failures by cause (gateway, DB, worker). This tells you whether to look at the payment gateway, the DB, or our own service first.

**Alert 2 - Pod stuck not ready**
- Threshold: a pod has been failing readiness for more than 5 minutes.
- Severity: warn the team (not a page unless many pods are affected).
- Runbook first step: `kubectl describe pod` and check the readiness probe error. Most often it is the DB pool or a missing config; if it is a real DB outage, escalate to Alert 1.

The two alerts cover different layers. Alert 1 is what users feel. Alert 2 is infrastructure. Both can fire alone or together, and the runbook tells you which one to follow first.