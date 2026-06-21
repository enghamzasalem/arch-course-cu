**part2\_health\_and\_rollout**

1. **The Observability Hooks:** We implement two distinct "Probes" to let Kubernetes know how the app is feeling.

* **Liveness Probe:**
* **Path:** GET /healthz/live
* **Logic:** A simple "Ping" to the Python interpreter.
* **Failure Action:** If the app deadlocks (e.g., a thread hang), the probe fails 3 times, and K8s **restarts** the container.
* **Readiness Probe:**
* **Path:** GET /healthz/ready
* **Logic:** It attempts a SELECT 1 on the PostgreSQL database and checks if the /app/uploads directory is writable.
* **Failure Action:** If the database is under heavy load and timing out, K8s **stops sending traffic** to this Pod but does not kill it. This prevents users from seeing "500 Internal Server Error" pages.

1. Rolling Updates: v1.4.0 to v1.5.0:

The "Before" state involved stopping the server (downtime). The "After" state uses a **Rolling Update**:

1. **Surge:** K8s creates one new Pod with the v1.5.0 image.
2. **Validation:** The cluster keeps the new Pod in a "Pending" state until the **Readiness Probe** returns a 200 OK.
3. **Substitution:** Once the new Pod is ready, K8s tells the Load Balancer to send it traffic and simultaneously begins terminating one old v1.4.0 Pod.
4. **Safety:** If v1.5.0 has a code error that prevents it from connecting to the DB, the Readiness Probe fails. The rollout **pauses automatically**. Your production environment remains on v1.4.0, and zero users are affected by the bad code.

1. Real Incident Detection & Recovery: If a "logical" bug (e.g., the "Checkout" button doesn't work but the app is "healthy") makes it through:

* **Detection:** We monitor **CloudWatch/Prometheus** for a drop in "Successful Orders" or a spike in 4xx/5xx status codes.
* **Recovery:** We don't try to "fix and redeploy." We immediately revert to the last known good state.
* **Command:** kubectl rollout undo deployment/citybite-api. This re-activates the previous **ReplicaSet**, bringing back the stable containers in roughly 10–20 seconds.