# Part 1: Deployability Assessment — CityBite on Kubernetes

**Target platform:** Amazon Elastic Kubernetes Service (EKS)
**Author:** kg
**Course context:** Chapter 9 — Deployability, Portability, and Containers

---

## 1. Deployability Risks in the Current Baseline

The table below identifies five concrete pain points in CityBite's present VM-based model, maps each to the root cause, and proposes the specific Kubernetes mechanism that mitigates it.

| # | Risk / Bottleneck | Root Cause | Kubernetes / Container Mitigation |
|---|---|---|---|
| 1 | **Snowflake hosts** | SSH-based deploys accumulate undocumented manual changes per VM over time; no two hosts are identical | Replace with **immutable container images** built in CI and pinned by digest in the Deployment manifest (`image: citybite-api@sha256:…`). Every pod runs the exact same filesystem; host state is irrelevant. |
| 2 | **Secrets committed to version control** | `.env` files were edited on disk per VM; engineers sometimes committed them to speed up onboarding | Move all secrets into **AWS Secrets Manager** and inject them at pod startup via the AWS Secrets and Configuration Provider (ASCP) as Kubernetes `Secret` objects; the `.env` pattern is abolished entirely. `DATABASE_URL`, `AWS_REGION`, etc. never appear in source control. |
| 3 | **Restart-causes-downtime deploys** | Monolith is restarted in-place on the VM; traffic is lost while the process is not listening | Use a Kubernetes **RollingUpdate** strategy (`maxUnavailable: 0`, `maxSurge: 1`). New pods are started and pass readiness probes before old pods are terminated; customers see zero interruption. |
| 4 | **No fast rollback path** | SSH deploy scripts overwrite binaries in place; reverting means re-running the old script manually | Each image tag is immutable and stored in ECR. Rollback is `kubectl rollout undo deployment/citybite-api`, which re-deploys the previously-pinned digest in under a minute. No manual SSH required. |
| 5 | **Menu images on local VM disk** | JPEGs stored under `/var/citybite/uploads` are inaccessible to any pod that was not the one that received the upload | Mount an **Amazon EFS PersistentVolumeClaim** (ReadWriteMany) into every API pod at the path specified by `DATA_DIR`. All pods share the same directory; uploads made through any pod are immediately visible to all others. |

---

## 2. Detailed Risk Descriptions

### Risk 1 — Snowflake Hosts

Over months of production operation, engineers applied hotfixes directly over SSH: patching library versions, editing cron schedules, adjusting kernel parameters. The result is a fleet of VMs that diverge silently. A deploy that works on host A may behave differently on host B. This also makes capacity scaling unsafe — a new VM added during a dinner spike may be missing a patch already applied to older hosts.

**Mitigation in detail:** CI (GitHub Actions) builds a single `Dockerfile` on every merge to `main`. The resulting image is pushed to Amazon ECR and the Deployment manifest is updated to the new digest. Every pod in the cluster — including pods scheduled on new nodes added by the Cluster Autoscaler — runs an identical binary with identical dependencies. Host drift is structurally impossible.

```dockerfile
# Dockerfile (sketch)
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "citybite.api:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

### Risk 2 — Secrets in Version Control

When a new developer joined, the quickest way to get a working environment was to copy `.env` from a senior engineer — sometimes via email or a shared Slack message. Over time, `.env.production` appeared in git history. Rotating the `DATABASE_URL` password now requires auditing all clones.

**Mitigation in detail:** Secrets are stored exclusively in AWS Secrets Manager. The ASCP syncs them into native Kubernetes `Secret` objects at pod startup. Pods consume secrets as environment variables injected by the platform — developers never see production values, and rotation in Secrets Manager propagates automatically on the next rollout.

```yaml
# env section of citybite-api Deployment
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: citybite-prod-secrets
        key: database_url
  - name: PORT
    value: "8080"
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef:
        name: citybite-config
        key: log_level
  - name: DATA_DIR
    value: "/mnt/uploads"
  - name: AWS_REGION
    value: "eu-central-1"
```

---

### Risk 3 — Restart-Causes-Downtime Deploys

The monolith binds to port 80 on a single VM. Restarting the process (required for any code change) drops all in-flight requests. During evening dinner spikes this is visibly noticed by customers and flagged in support tickets. Marketing campaigns that drive traffic make deploy windows unpredictable.

**Mitigation in detail:** Kubernetes's RollingUpdate strategy ensures at least one old pod is serving traffic until at least one new pod passes its readiness probe. The readiness probe hits `/health/ready`, which verifies the database connection is live before the pod is admitted to the Service's endpoint list.

```yaml
# Deployment strategy + probes (sketch)
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5

livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 10
```

---

### Risk 4 — No Fast Rollback

The current SSH deploy script overwrites binaries in `/opt/citybite`. There is no preserved artifact of the previous version on the VM. Rolling back means locating the last release tarball, copying it back, and restarting — a 10–20 minute manual procedure done under pressure during an outage.

**Mitigation in detail:** ECR retains every tagged image indefinitely. Kubernetes preserves the last ten `ReplicaSet` revisions by default (`revisionHistoryLimit: 10`). Any revision can be restored with a single command, which re-applies the original Deployment spec including the pinned image digest. The rollback completes in the time it takes for pods to pass their readiness probe — typically under two minutes.

---

### Risk 5 — Menu Images on Local Disk

Restaurant partners upload menu photos through the tablet app. Today these are saved to `/var/citybite/uploads` on whatever VM handled the upload request. If a subsequent request for the image is load-balanced to a different VM, it returns a 404. The workaround has been sticky sessions, which defeats load balancing and complicates the scaling story.

**Mitigation in detail:** An EFS PersistentVolume is provisioned with `accessModes: [ReadWriteMany]` and mounted into every API pod at `$DATA_DIR` (`/mnt/uploads`). Sticky sessions are removed from the load balancer. All pods share one consistent view of the filesystem. Uploads are also replicated across EFS availability zones by default, removing the single-disk failure risk.

```yaml
# PVC for shared uploads
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: citybite-uploads-pvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: efs-sc
  resources:
    requests:
      storage: 50Gi
```

---

## 3. One Thing That Becomes Harder

### Local Reproduction of Distributed Failures

**The problem:** On the old monolith, a developer could reproduce any production bug by running one process locally with one `.env` file. After the Kubernetes migration, CityBite has multiple services (API, background job worker, dispatch dashboard backend). A failure might involve the interaction between a pod's readiness probe timing and a slow database connection during startup — not reproducible by running `python app.py` alone.

**How it manifests:** An engineer sees a `CrashLoopBackOff` in production but cannot reproduce it locally because their laptop never exercises Kubernetes liveness/readiness logic, and their local Postgres is never under the same connection-pool pressure as RDS.

**Mitigation:**
1. **Docker Compose parity environment.** Maintain a `docker-compose.yml` that mirrors the production topology: API container, worker container, local Postgres, and a MinIO container standing in for EFS. The compose file uses the same environment variable names (`DATABASE_URL`, `PORT`, `DATA_DIR`, `LOG_LEVEL`) so config parity is structural, not aspirational.
2. **Structured logs surfaced locally.** The API emits JSON logs at all levels, including probe hit/miss events. Developers run `docker compose logs -f` to observe the exact same log lines they would see via `kubectl logs`.
3. **Runbook for probe debugging.** A short `CONTRIBUTING.md` section explains how to simulate a slow database (`tc netem` or a sleep in the compose healthcheck) to exercise the readiness probe locally before pushing.

---

