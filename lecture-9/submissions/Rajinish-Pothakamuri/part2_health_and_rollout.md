## Part 2: Health, Rollout, and Failure

### 1. Health Probes for CityBite API

To ensure the orchestrator (Kubernetes) correctly manages the lifecycle of the Order API, we define two distinct probes. These probes allow the cluster to distinguish between a service that is starting up, a service that is temporarily busy, and a service that has completely failed.

| Probe Type | Mechanism | Configuration | Purpose |
| :--- | :--- | :--- | :--- |
| **Liveness** | HTTP GET `/health/live` | `periodSeconds: 10`, `failureThreshold: 3` | Determines if the container needs to be restarted due to a deadlock or crash. |
| **Readiness** | HTTP GET `/health/ready` | `initialDelaySeconds: 15`, `successThreshold: 1` | Determines if the container is ready to accept traffic (e.g., DB connection is established). |

**Liveness vs. Readiness Logic**
* **Liveness**: Returns a simple `200 OK` if the process is responsive. If this fails three times, Kubernetes kills the pod and starts a new one.
* **Readiness**: Performs a lightweight check on the PostgreSQL connection and S3 connectivity. If this fails, the pod is removed from the Service endpoints so no customers receive errors, but the pod is not killed.

---

### 2. Rolling Update Process (v1.4.0 to v1.5.0)

When a new version of CityBite is deployed, Kubernetes uses a **Rolling Update** strategy to ensure zero downtime.

**Step-by-Step Execution:**
1. **Trigger**: The deployment manifest is updated with the new image tag `citybite-api:v1.5.0`.
2. **New ReplicaSet**: Kubernetes creates a new ReplicaSet for `v1.5.0` and begins spinning up the first new pod.
3. **Readiness Check**: The new pod must pass its **Readiness Probe** before it is considered "available".
4. **Traffic Shift**: Once the new pod is ready, the Kubernetes Service begins routing a portion of production traffic to it.
5. **Incremental Replacement**: Kubernetes terminates one old `v1.4.0` pod. This cycle continues until all pods are running `v1.5.0`.

**Failure Scenario:**
If the `v1.5.0` pods fail their readiness probes (e.g., due to a code bug or missing environment variable), the rolling update will halt. The cluster will stop creating new pods and keep the remaining `v1.4.0` pods active, preventing a total outage.

---

### 3. Real Incident Detection and Rollback

**Detection**
During a deployment, we monitor the **CloudWatch Logs** and **Container Metrics**. We look specifically for:
* A spike in `5xx` HTTP errors.
* The `Ready` count in the deployment staying below the desired replicas for more than 5 minutes.
* OOMKill (Out of Memory) events on the new pods.

**Rollback Procedure**
If the deployment is deemed unhealthy, we execute a manual or automated rollback to the last known good state.
* **Command**: `kubectl rollout undo deployment/citybite-api`
* **Action**: This command tells the Kubernetes control plane to switch back to the previous stable **ReplicaSet**.
* **Result**: The cluster immediately begins terminating the bad `v1.5.0` pods and scaling the proven `v1.4.0` pods back up to full capacity.