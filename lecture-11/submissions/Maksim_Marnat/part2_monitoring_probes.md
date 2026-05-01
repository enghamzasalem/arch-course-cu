# Part 2.1 — Monitoring & probes (Order API on Kubernetes)

## 1. Liveness vs readiness (Order API)

| Probe | Path / check | What it proves | If it fails |
|-------|----------------|----------------|-------------|
| **Liveness** | e.g. `GET /internal/livez` — cheap: process responds, no deadlock in probe handler | The **Python/ JVM process** is not wedged; pod should be **restarted** by kubelet if failing repeatedly. | Kubelet **restarts** the container after `failureThreshold` (nuke wedged workers). |
| **Readiness** | e.g. `GET /internal/readyz` — **deep**: acquire DB connection from pool within timeout, optional “SELECT 1”, optional “can reach PSP health endpoint” with tight timeout | The pod can **accept new sessions** and complete checkout-shaped work—aligned with **deep readiness** in `example2_availability_monitoring_citybite.py` (shallow `True` vs pool exhaustion). | Pod **removed from Service endpoints**; **no new traffic**; existing connections drain; no restart unless liveness also fails. |

**Failure actions:** liveness bad → **restart**; readiness bad → **remove from load balancer** (keep process up for debugging / drain).

## 2. Why “200 OK on `/healthz`” can lie (`example2`)

In `example2_availability_monitoring_citybite.py`, **`shallow_health()` always returns `True`** while the fake DB pool is exhausted—exactly like an empty `/healthz` that only checks “is my web server thread alive”. The load balancer still sends traffic; new requests pile onto pods that **cannot obtain DB connections**, increasing latency and failure rates **user-visible** SLIs tank while Kubernetes thinks the pod is fine.

**Readiness** must approximate **“can we take an order now?”**—e.g. try-acquire from pool with short timeout (`deep_readiness`), not a trivial boolean.

## 3. Synthetic check (black-box, outside cluster)

**Probe:** Scheduled **synthetic transaction** from a neutral runner (e.g. synthetic monitoring SaaS in another region) hitting **staging or prod-like canary**:  

- Authenticate test account → build cart → **call checkout API with test PSP credentials** (sandbox) → assert **201 + order id + payment state**.

**Asserts:** end-to-end path including **ingress TLS**, **Order API**, **DB**, and **PSP test endpoint**—closer to customer-visible availability than in-cluster kube ping.

## 4. Alerting (two alerts)

| Alert | Threshold | Runbook first step |
|-------|-----------|---------------------|
| **Checkout SLI burn** | Multi-window: e.g. **5% error rate over 15m** **and** **2× burn vs 1h baseline** on “place paid order” success ratio | **Page on-call**; open incident channel; check **PSP status page** and recent Order API / payment adapter deploys; consider **rollback** if correlated. |
| **Readiness flapping** | **>30% of Order API pods** not ready **or** readiness failure rate **>10/min** for 5m | **Do not scale out blindly**; inspect DB connections, pool metrics, **recent deploy**; if DB incident, engage DBA / failover playbook; scale only if DB healthy. |
