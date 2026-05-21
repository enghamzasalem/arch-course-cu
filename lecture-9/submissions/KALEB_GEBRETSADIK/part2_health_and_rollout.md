# Part 2: Containers and Runtime Contract

## Task 2.2: Health, Rollout, and Failure

### 1. Liveness vs Readiness Probes

To ensure robust operability and zero-downtime routing, the Order API pods explicitly define two distinct HTTP probe contracts within their Kubernetes deployment context:

**Readiness Probe:**
*   **Purpose:** Determines if the specific pod is fully booted and ready to instantly receive active user traffic from the Ingress Controller / K8s Service.
*   **Implementation:** HTTP GET `/health/ready`
*   **Internal Logic:** The API executes a lightweight `SELECT 1` query to verify that the connection to the external Managed PostgreSQL database is positively active.
*   **Thresholds:** `initialDelaySeconds: 5`, `periodSeconds: 10`, `failureThreshold: 3`.
*   **Behavior on Failure:** If the database connection drops for this pod specifically, it fails the probe 3 times. Kubernetes instantly removes the pod's IP from the Service load balancer so no customer encounters a failed checkout, but it explicitly **does not kill** the pod (allowing the transient DB network blip to recover natively).

**Liveness Probe:**
*   **Purpose:** Determines if the primary Python execution thread has permanently frozen, deadlocked, or crashed into a zombie state.
*   **Implementation:** HTTP GET `/health/live`
*   **Internal Logic:** Immediately returns an empty `200 OK`. It absolutely does not check the database. It solely verifies that the Uvicorn web loop is actively accepting and answering HTTP threads.
*   **Thresholds:** `initialDelaySeconds: 15`, `periodSeconds: 15`, `failureThreshold: 3`. 
*   **Behavior on Failure:** If the application is totally frozen resulting in a failure to reply, the kubelet will actively send `SIGTERM` followed by `SIGKILL` to explicitly reboot the container from scratch.

---

### 2. Rolling Update Execution (`v1.4.0` → `v1.5.0`)

When a developer seamlessly applies a new Kubernetes manifest shifting the image explicitly from `v1.4.0` to `v1.5.0`, the cluster coordinates a safe **Rolling Update**:
1. The Kubernetes controller provisions a brand-new `ReplicaSet` specifically for the `v1.5.0` containers. The existing `v1.4.0` `ReplicaSet` is left totally untouched and continues completely serving active consumer traffic.
2. The orchestrator spins up the first batch of `v1.5.0` Pods (based on constraints like `maxSurge` / `maxUnavailable`).
3. **If new pods pass Readiness:** Once the `v1.5.0` containers successfully answer their Readiness Probes, Kubernetes places them cleanly onto the active Service router, and subsequently gracefully signals the old `v1.4.0` pods to terminate. This cycle repeats transparently until 100% of the fleet is functionally running `v1.5.0` with absolutely zero dropped user connections.
4. **If new pods fail Readiness:** If the new `v1.5.0` code immediately crashes or breaks external DB connections, the Readiness Probes will fail permanently. Kubernetes completely halts the rollout. Crucially, the cluster refuses to route *any* production traffic into that broken subset of `v1.5.0` pods, and explicitly refuses to terminate the surviving `v1.4.0` pods.

---

### 3. Real Incident Detection and Rollbacks

Assume a scenario where a destructive application logic bug bypassing the Readiness probes makes it into production (e.g., successfully reading DB connectivity but specifically crashing whenever users click "Checkout Order"). Operations engineers will implicitly detect this failure because the centralized Prometheus / CloudWatch aggregated log metrics will show a massive sudden spike in HTTP 500 error rates strictly associated with the new release tag. 

Because K8s deployments strictly map declarative history to explicitly preserved ReplicaSets, tracing back is trivial. An engineer instantly executes `kubectl rollout undo deployment/citybite-order-api` against the EKS cluster. Kubernetes immediately scales up the prior preserved `ReplicaSet` running exactly the `v1.4.0` image digest format, transparently cutting away traffic from the faulty containers and stopping the outage in seconds without executing complex CI rollbacks or manual SSH maneuvers.
