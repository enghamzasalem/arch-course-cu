# Part 2.2 – Health, Rollout, and Failure

## Probes

| Probe | Path | Initial Delay | Period | Purpose |
|-------|------|---------------|--------|---------|
| **Readiness** | `/ready` | 5s | 10s | Pod ready to receive traffic |
| **Liveness** | `/live` | 15s | 20s | Restart if deadlocked or stuck |

## Rolling Update (v1.4.0 → v1.5.0)

1. Kubernetes starts one new pod with image v1.5.0
2. New pod runs, readiness probe checks `/ready`
3. If ready, cluster terminates one old pod
4. Repeats until all pods are v1.5.0

**If new pod fails readiness:** Rollout pauses. Old pods continue serving traffic.

## Rollback Detection and Action

**Detection:**
- Monitor `kubectl rollout status deployment/citybite-api`
- Watch metrics: HTTP 5xx error rate exceeds 1%
- Alert from Cloud Monitoring

**Rollback:**
```bash
kubectl rollout undo deployment/citybite-api
```