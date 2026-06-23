# Part 2.1 — Monitoring & Probes

## Liveness vs Readiness (Order API)

### Liveness Probe
- Path: `/healthz`
- Purpose: Check if the application process is alive
- What it proves: The API is running (not crashed)

**Failure Action:**
- Kubernetes restarts the container

---

### Readiness Probe
- Path: `/ready`
- Purpose: Check if the service can handle requests
- What it proves:
  - Database connection is working
  - Dependencies are reachable

**Failure Action:**
- Pod is removed from load balancer (no traffic sent)

---

## Why Simple Health Checks Can Lie

A simple `/healthz` returning "200 OK" does NOT guarantee the system is usable.

Example:
- DB connection pool is exhausted
- API is running → returns 200
- But cannot process new requests

=> This is why **readiness checks must be deeper**
(as shown in `example2`)

---

## Synthetic Monitoring (Black-box)

Example:
- Simulate "place order" from outside the system

What it checks:
- API availability
- Database response
- Payment flow (basic)

=> This reflects **real user experience**

---

## Alerting

### Alert 1: High Error Rate
- Condition: Error rate > 5% for 5 minutes
- Action:
  - Check logs
  - Identify failing service (API / DB / external)

---

### Alert 2: High Latency
- Condition: p95 latency > 2 seconds
- Action:
  - Check database load
  - Check API CPU usage
  - Verify external services (payment, maps)

---

## Why Monitoring Matters

Monitoring must reflect **user experience**, not only system health.

A system can be "running" but still unusable for customers.