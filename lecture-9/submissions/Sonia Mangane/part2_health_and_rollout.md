# Task 2.2: Health, Rollout, and Failure

## 2.1 Probes
* **Readiness Probe:** `GET /health/ready`. Checks connectivity to Postgres. If it fails, K8s removes the Pod from the Service endpoint so customers don't see 500 errors.
* **Liveness Probe:** `GET /health/live`. A simple "heartbeat." If the process deadlocks, K8s kills and restarts the container.

## 2.2 Rolling Update Scenario (v1.4.0 -> v1.5.0)
When the image is updated, Kubernetes:
1.  Starts a new Pod with `v1.5.0`.
2.  Waits for the **Readiness Probe** to pass.
3.  If successful, it directs traffic to the new Pod and terminates one `v1.4.0` Pod.
4.  **Failure Handling:** If `v1.5.0` crashes or fails probes, K8s halts the rollout, leaving the remaining `v1.4.0` pods to handle traffic.

## 2.3 Incident Response
Detection via CloudWatch Alarms on 5XX error rates. Rollback is triggered via:
`kubectl rollout undo deployment/citybite-api`
This restores the previous `ReplicaSet` immediately.