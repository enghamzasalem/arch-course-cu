# Part 2 — Monitoring and Probes (CityBite)

## 1. Overview

CityBite relies on monitoring, health probes, and alerting to maintain availability during traffic spikes and dependency failures. In Kubernetes, health checks are important because a container may still be running even when it cannot successfully process customer requests.

This section explains how CityBite uses liveness checks, readiness checks, synthetic monitoring, and operational alerts to detect failures early and reduce downtime.

---

## 2. Liveness vs Readiness Probes

Kubernetes uses two different probe types for the Order API.

---

### 2.1 Liveness Probe

### Purpose
The liveness probe checks whether the application process is still running correctly.

If the probe repeatedly fails:
- Kubernetes restarts the container automatically
- The goal is to recover from deadlocks or crashed processes

---

### Example Configuration

| Setting | Value |
|----------|------|
| Endpoint | `/health/live` |
| Method | HTTP |
| Interval | Every 10 seconds |
| Failure Threshold | 3 failures |
| Action on Failure | Restart container |

---

### What It Actually Proves

The liveness probe only proves:
- The application process is alive
- The HTTP server can respond

It does **not** guarantee the API can successfully serve orders.

---

## 2.2 Readiness Probe

### Purpose
The readiness probe determines whether the pod is capable of handling real traffic.

If readiness fails:
- Kubernetes removes the pod from Service endpoints
- Traffic is no longer routed to that pod
- The container itself continues running

---

### Example Configuration

| Setting | Value |
|----------|------|
| Endpoint | `/health/ready` |
| Method | HTTP |
| Interval | Every 5 seconds |
| Failure Threshold | 3 failures |
| Action on Failure | Remove from load balancer |

---

### What It Proves

The readiness probe verifies:
- Database connectivity is available
- Critical dependencies are reachable
- Connection pools are not exhausted
- The API can process requests successfully

---

## 3. Why “200 OK” Can Be Misleading

The lecture example demonstrated that a shallow health endpoint can incorrectly report success even when the application is effectively unusable.

For example:
- The Python process may still respond with `200 OK`
- However, the database connection pool may already be exhausted
- New requests would fail despite the pod appearing healthy

This is why CityBite uses a deeper readiness check that attempts lightweight access to critical resources such as:
- Database connection acquisition
- Redis connectivity
- Queue availability (optional)

The goal is to measure whether the service is truly capable of handling user traffic, not simply whether the process is alive.

---

## 4. Synthetic Monitoring

CityBite also uses external synthetic checks from outside the Kubernetes cluster.

### Example Synthetic Test

A monitoring service periodically:
1. Opens the customer app homepage
2. Searches for a restaurant
3. Sends a lightweight test checkout request
4. Verifies the API returns a successful response within an acceptable latency threshold

---

### Why Synthetic Checks Matter

Internal probes only test local service health.

Synthetic monitoring verifies:
- DNS resolution
- CDN availability
- TLS certificates
- Ingress routing
- Real user request flow

This provides a more realistic measurement of customer experience.

---

## 5. Alerting Strategy

CityBite defines operational alerts with clear thresholds and immediate response actions.

---

## Alert 1 — High Checkout Failure Rate

| Metric | Threshold |
|--------|-----------|
| Checkout failure rate | Above 5% for 5 minutes |

### First Runbook Step
- Check payment gateway status dashboard
- Review recent deployments
- Inspect circuit breaker metrics

---

## Alert 2 — Database Connection Pool Exhaustion

| Metric | Threshold |
|--------|-----------|
| DB pool utilization | Above 90% for 10 minutes |

### First Runbook Step
- Identify slow queries
- Inspect API pod scaling behavior
- Temporarily increase connection pool limits if safe

