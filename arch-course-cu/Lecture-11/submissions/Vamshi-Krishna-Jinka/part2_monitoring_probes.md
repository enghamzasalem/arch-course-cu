# Part 2: Monitoring & Failure Containment
## Task 2.1: Monitoring & Probes

## 1. Overview
CityBite should monitor whether the Order API process is alive and whether it is actually able to serve real requests. A pod that is running is not always a healthy service, especially when the database pool is exhausted or a downstream dependency is failing. This is the same lesson shown in the lecture example about shallow health versus deep readiness: a simple `200 OK` can lie if the service cannot really take traffic. fileciteturn4file0

---

## 2. Liveness vs Readiness for the Order API

### Liveness probe
- **Path:** `GET /healthz`
- **What it proves:** The process is running and the HTTP server is responsive.
- **Failure action:** Kubernetes restarts the container if the probe fails repeatedly.

### Readiness probe
- **Path:** `GET /readyz`
- **What it proves:** The Order API can actually serve requests, including critical dependencies such as the DB connection pool and any required local resources.
- **Failure action:** Kubernetes removes the pod from the load balancer until it becomes ready again.

### Why both are needed
Liveness answers “should this process be restarted?” Readiness answers “should this pod receive traffic right now?” This separation prevents Kubernetes from sending requests to a pod that is alive but unable to complete checkouts.

---

## 3. Why `200 OK` on `/healthz` can lie

A shallow health endpoint may return `200 OK` as long as the web server process is up. But the service can still be unusable if the DB connection pool is exhausted, a lock is stuck, or downstream calls are timing out. The lecture example demonstrates this directly: the process can answer `/healthz` while readiness fails because it cannot acquire a DB-like resource. fileciteturn4file0

For CityBite, this means a pod may look green in Kubernetes while checkout requests are still timing out. The fix is to keep liveness shallow and make readiness test the critical path.

---

## 4. Synthetic Check from Outside the Cluster

### Probe
A black-box synthetic check should run from outside the cluster every minute:

- Call `POST /api/v1/orders` with a small test cart and a test account
- Assert that the response is successful within a latency threshold
- Verify that the order appears in a test-only dashboard or status endpoint
- Clean up or mark the test order so it does not affect real operations

### What it asserts
This probe checks the real user journey, not just the process state. It confirms that the API, database, and basic order path are working together from the user’s point of view.

---

## 5. Alerts and Runbook First Steps

### Alert 1: Checkout success rate drops
- **Threshold:** successful checkout rate below 99.5% for 5 minutes
- **Why it matters:** This is the most important user-visible journey
- **Runbook first step:** Check whether the issue is caused by the payment gateway, DB errors, or a recent deployment

### Alert 2: Readiness failures or DB pool exhaustion
- **Threshold:** more than 20% of Order API pods are not ready for 3 minutes, or DB connection pool usage stays above 90% for 5 minutes
- **Why it matters:** This usually means traffic is hitting a half-dead service
- **Runbook first step:** Stop sending traffic to unhealthy pods, inspect DB saturation, and check whether retries are causing extra load

---

## 6. Summary
CityBite should treat liveness and readiness as different signals. Liveness protects uptime by restarting dead processes, while readiness protects users by removing unhealthy pods from traffic. A black-box synthetic check and a small number of sharp alerts make it easier to detect real availability problems before customers notice them.
