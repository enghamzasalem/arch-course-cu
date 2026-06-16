# Part 2.2 — Health, rollout, rollback

## Probes — Order API

| Probe | Mechanism | Purpose |
|-------|-----------|---------|
| **Liveness** | HTTP `GET /health/live` every **10s**, `timeoutSeconds: 2`, `failureThreshold: 3` | Process is not deadlocked; **restart** pod if it hangs after DB blip. |
| **Readiness** | HTTP `GET /health/ready` every **5s**, `initialDelaySeconds: 15`, `failureThreshold: 6` | App can accept traffic: **DB pool** and **S3 IAM** checks OK; **remove from Service endpoints** if not ready. |

**Why different:** Liveness must not flap on slow RDS; readiness should drop **before** users hit 500s during dependency outage.

TCP-only probes are avoided so we distinguish “port open” from “can serve orders.”

## Rolling update `v1.4.0` → `v1.5.0`

1. **Deployment** `image: …:v1.5.0` applied; controller creates **new ReplicaSet**.
2. **Rolling strategy** (e.g. `maxSurge: 1`, `maxUnavailable: 0`): new pods start; old stay until new pass **readiness**.
3. If **new pods never become Ready** (crash loop or readiness fails): new ReplicaSet **does not** receive traffic; old pods **keep serving** `v1.4.0` (no surge of errors if `maxUnavailable: 0`).
4. When new pods Ready, **Endpoints** update; ALB targets drain gracefully; old pods terminate after `terminationGracePeriod`.

## Incident: bad deploy — detect and roll back

After promoting `v1.5.0`, **5xx rate** and **latency** climb on the **ALB target group**; **CloudWatch** alarm fires. On-call checks **ECR** tag and **Deployment** revision, confirms correlation with release. **Rollback:** `kubectl rollout undo deployment/citybite-order-api -n citybite` (or set `image` to last known digest from **previous ReplicaSet**). **Root cause** in parallel: compare **structured error logs** (`payment`, `db`) and run **staging** replay. Post-incident: require **canary** or **manual soak** on staging EKS before prod promotion.
