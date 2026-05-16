# Part 2.2: Health, Rollout, and Failure — CityBite Order API

---

## 1. Liveness vs Readiness Probes

The two probe types serve distinct purposes and must not be conflated. A **readiness probe** answers "is this pod ready to receive traffic right now?" — the Service endpoint controller adds or removes the pod from the load-balancing pool based on its result. A **liveness probe** answers "is this process still alive and making progress?" — a failing liveness probe causes the kubelet to restart the container, which is a more disruptive action and should only trigger when the process is genuinely stuck.

### Readiness probe

```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
  successThreshold: 1
  timeoutSeconds: 2
```

`/health/ready` performs two lightweight checks: it verifies that the database connection pool has at least one available connection (a `SELECT 1` against `DATABASE_URL`) and that the EFS mount at `DATA_DIR` is reachable (a `stat` on the mount path). If either check fails, the endpoint returns HTTP 503 and the pod is removed from the Service's endpoint list within one probe cycle (5 s). `initialDelaySeconds: 5` gives Uvicorn time to complete startup before the first check. Three consecutive failures are required before the pod is considered unready, preventing a single slow database response from causing a false removal.

### Liveness probe

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
  successThreshold: 1
  timeoutSeconds: 3
```

`/health/live` returns HTTP 200 if the Uvicorn event loop is responsive. It does **not** check the database — a database outage should make the pod unready (no traffic), not trigger a container restart (which would accomplish nothing while the database is down). `initialDelaySeconds: 15` is longer than the readiness delay to prevent the kubelet from restarting a pod that is still initialising on first boot. Three failures across 30 seconds are required before a restart is triggered, which avoids restarting a pod experiencing a brief but recoverable latency spike.

### Startup probe (supplementary)

For releases that include a database migration on startup, a startup probe is also declared:

```yaml
startupProbe:
  httpGet:
    path: /health/live
    port: 8080
  failureThreshold: 12
  periodSeconds: 5
```

This gives the process up to 60 seconds to complete migrations before liveness checking begins. Without it, a migration that runs longer than `initialDelaySeconds` would trigger a liveness restart loop.

---

## 2. Rolling Update: v1.4.0 to v1.5.0

### Deployment strategy configuration

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1
```

With `replicas: 3`, `maxUnavailable: 0` means the cluster must keep all three v1.4.0 pods serving traffic throughout the rollout. `maxSurge: 1` allows one extra pod above the desired count, so a fourth pod (v1.5.0) is created before any old pod is removed.

### Step-by-step sequence

1. The CI pipeline pushes `citybite-api:v1.5.0` to ECR and updates the Deployment manifest with the new digest. `kubectl apply` is run (or ArgoCD detects the change and syncs).
2. The Deployment controller creates **Pod D** running v1.5.0. All three v1.4.0 pods remain in service — the cluster is temporarily at 4 pods.
3. Pod D's readiness probe begins polling `/health/ready` every 5 seconds. While it is not yet ready, zero traffic is sent to it.
4. Once Pod D passes readiness (successive 200 responses), it is added to the Service endpoint list. The cluster now has 4 healthy pods.
5. The controller terminates **Pod A** (v1.4.0). It sends `SIGTERM`; Uvicorn drains in-flight requests within the 30-second graceful shutdown window, then exits. The cluster is back to 3 pods, one of which is v1.5.0.
6. Steps 2–5 repeat for Pod B and Pod C until all three replicas run v1.5.0.

Throughout the rollout, at least 3 pods are serving traffic. Customer-facing downtime is zero provided the new image passes its readiness probe.

### What happens if v1.5.0 pods fail readiness

If Pod D never passes `/health/ready` — for example because v1.5.0 introduced a misconfigured `DATABASE_URL` or a bug in the startup path — the rollout stalls. The controller does not proceed to terminate any v1.4.0 pods. All three v1.4.0 pods remain in the Service endpoint list and continue serving traffic normally.

Pod D enters a `CrashLoopBackOff` or stays in `0/1 Ready` state. The rollout remains paused indefinitely, or until the Deployment's `progressDeadlineSeconds` (default 600 s) is exceeded, at which point the Deployment is marked `ProgressDeadlineExceeded`. No customer traffic is affected because `maxUnavailable: 0` prevented any old pod from being removed.

---

## 3. Detecting and Rolling Back a Bad Deploy

After the rollout to v1.5.0 completes successfully (all pods pass readiness), a latent bug may only surface under real traffic. The detection signal comes from two sources: CloudWatch Container Insights reports a spike in HTTP 5xx responses on the `citybite-api` Service within minutes of the rollout completing, and the p99 latency metric in the CityBite application dashboard crosses the SLO threshold. An on-call engineer confirms the correlation with the deploy timestamp in the CI pipeline. Recovery is a single command:

```bash
kubectl rollout undo deployment/citybite-api -n citybite-prod
```

Kubernetes re-applies the previous ReplicaSet (which references the `v1.4.0` image digest retained in ECR) using the same rolling strategy — `maxUnavailable: 0`, `maxSurge: 1` — so the rollback itself is zero-downtime. The previous ReplicaSet is available because `revisionHistoryLimit: 10` is set on the Deployment, preserving the last ten ReplicaSet revisions. The rollback typically completes within 90 seconds; the 5xx rate returns to baseline as each v1.4.0 pod passes its readiness probe and re-enters the Service endpoint list.
