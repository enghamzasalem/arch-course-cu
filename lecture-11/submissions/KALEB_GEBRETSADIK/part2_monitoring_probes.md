# Part 2.1: Monitoring & Probes

**Liveness vs. Readiness for Order API:**
- **Liveness Probe (`/healthz/liveness`):** Asserts the process is alive (e.g., threads are not deadlocked). **Failure Action:** Kubernetes restarts the pod.
- **Readiness Probe (`/healthz/readiness`):** Asserts the pod is fully initialized and can reach dependencies (e.g., database). **Failure Action:** Kubernetes removes the pod from the Load Balancer so it stops receiving traffic.

**Contrast with `example2` (Shallow Health vs Deep Health):**
A shallow "200 OK" on `/healthz` may respond successfully even if the DB connection pool is exhausted. It lies because it doesn't test the actual dependencies required to serve requests. A true readiness probe must perform a lightweight check on critical dependencies.

**Synthetic Check (Black-Box Probe):**
A script running outside the cluster simulates a user login and checkout with a mock payment card. It asserts that the entire flow returns a 200 OK within 2 seconds. This proves user-visible availability across all layers (Ingress, API, DB).

**Alerting:**
1. **High Checkout Latency Alert:**
   - **Threshold:** 95th percentile latency of `/checkout` > 3s for 5 minutes.
   - **Runbook First Step:** Check payment gateway latency metrics to see if it's external, then verify if circuit breakers are open.
2. **Database Connection Pool Exhaustion:**
   - **Threshold:** Active DB connections > 90% of max capacity for 3 minutes.
   - **Runbook First Step:** Identify and kill slow queries blocking connections.
