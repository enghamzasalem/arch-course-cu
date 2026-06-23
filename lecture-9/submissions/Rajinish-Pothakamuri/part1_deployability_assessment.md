# Part 1: Deployability Assessment: CityBite on Kubernetes

## Target Cloud: Amazon Web Services (EKS)

All references to cloud-specific services in this document use AWS.
Managed Postgres runs on **Amazon RDS**; container images are stored in **Amazon ECR**;
object storage (where relevant) uses **S3**. The Kubernetes distribution is **Amazon EKS**.

---

## 1.1 Current Pain Points and Proposed Mitigations

### Risk 1: Snowflake Hosts (Host Drift)

**What is happening today.**
Deploys happen over SSH using shell scripts. Over time, each VM accumulates small differences — an extra package installed by hand, a slightly different kernel version, a `.env` file that someone edited to debug a production issue and never reverted. When something breaks it is genuinely unclear whether the bug is in the code or in the host. Reproducing an issue locally is even harder because a developer's laptop never matched the VM exactly to begin with.

The deeper problem is that the *deployment artifact* and the *runtime environment* are managed separately and drift apart over months. There is no reliable inventory of what is actually running.

**Mitigation in Kubernetes.**
We build a **container image** in CI on every merged commit. The image bundles the application code, its Python runtime, and every library dependency into a single, content-addressable, immutable artifact. The Kubernetes Deployment references that image by **digest** (e.g. `ecr.aws/.../citybite-api@sha256:ab12…`), not by a mutable tag like `:latest`. Every Pod that starts from that Deployment spec runs exactly the same filesystem. There is no configuration to drift on the host because the "host" is a thin container runtime that the cluster manages, not a VM anyone SSHes into.

---

### Risk 2: Secrets in Git History

**What is happening today.**
The `.env` files that hold `DATABASE_URL`, payment API keys, and similar credentials live on disk per VM. At some point in the past (and probably again more recently than anyone admits) those files were committed to the application repo or a private config repo, ending up in git history. Rotating a leaked secret requires rewriting git history, which is painful and rarely done properly.

**Mitigation in Kubernetes.**
Secrets are stored in **AWS Secrets Manager** and surfaced to pods through the **AWS Secrets and Configuration Provider (ASCP)** mounted as in-memory volumes, or alternatively projected as environment variables via **Kubernetes Secrets** that are themselves synced from Secrets Manager by an External Secrets Operator. Neither the image nor the Kubernetes manifests in the git repo contain any secret values — they contain only references (e.g. the name of the secret in Secrets Manager). Rotation means updating the value in Secrets Manager and triggering a rolling redeploy; the old value is never in version control.

---

### Risk 3: Manual Deploys with No Rollback Path

**What is happening today.**
A deploy means SSHing into each VM, pulling new code, and restarting the process. If something is wrong with the new version there is no automated rollback. The operator has to SSH back in, check out the previous commit, and restart again, all while the site is down or degraded. The time from "we detected a problem" to "old version is running" is measured in minutes of manual work.

**Mitigation in Kubernetes.**
Kubernetes tracks **ReplicaSets**: every time a Deployment's pod template changes (e.g. a new image digest), the controller creates a new ReplicaSet and keeps the previous one around at zero replicas. Rolling back is a single command:

```
kubectl rollout undo deployment/citybite-api
```

or a GitOps commit reverting the image tag in the manifest. Kubernetes also performs the rollout progressively, it never terminates old pods before new pods pass their readiness probe, so a bad deploy that cannot serve traffic is caught before all old pods are gone. Rollback happens to a known-good, previously deployed image, not to a "hopefully the same state as git HEAD minus one."

---

### Risk 4: Menu Images on VM Local Disk

**What is happening today.**
Restaurant menu JPEGs are written to `/var/citybite/uploads` on whichever VM handled the upload request. If there are two VMs behind a load balancer, an image uploaded via VM-A is invisible to VM-B. Scaling horizontally is therefore broken by default. Worse, if a VM is replaced or reprovisioned the images are gone.

**Mitigation in Kubernetes.**
The application reads and writes menu images through the `DATA_DIR` environment variable. In the Kubernetes deployment this path is backed by an **Amazon S3 bucket** accessed via a lightweight adapter (or the AWS SDK called directly in the upload handler). S3 is durable, regionally replicated, and shared across every Pod regardless of which node it runs on. No Pod carries mutable state on local disk. A Pod crash or node replacement loses no uploads because the files were never on the Pod filesystem to begin with.

> An alternative would be a `PersistentVolumeClaim` backed by EFS (a shared, POSIX-compatible
> network filesystem on AWS). This keeps the `DATA_DIR` abstraction intact and requires no
> code change. The trade-off is cost and latency versus S3. This choice is explored further
> in Part 3.

---

### Risk 5: Monolith Restart Causes Minutes of Downtime

**What is happening today.**
Background jobs for dispatch retries, notification sends, and similar async work run inside the same process as the Order API. Restarting the monolith for any reason like deploy, crash, config change will kills both the HTTP server and all in-flight jobs simultaneously. Because restart is the only deployment mechanism and it takes time to boot, customers see errors for the duration.

**Mitigation in Kubernetes.**
The move to containers separates concerns along two axes:

1. **Multiple replicas with rolling updates.** The API Deployment runs with at least two replicas (`replicas: 3` during dinner-spike hours via a HorizontalPodAutoscaler). A rolling update replaces Pods one at a time; at no point are all replicas down simultaneously.

2. **Worker as a separate Deployment.** Dispatch-retry jobs move to a dedicated worker container (a separate Deployment or a CronJob depending on trigger semantics). The worker and the API can be deployed and restarted independently. An API deploy does not interrupt in-flight retries, and a worker crash does not take down the HTTP serving layer.

Together these two mechanisms eliminate the "restart everything to deploy anything" failure mode.

---

## 1.2 One Thing That Gets Harder

### Local Reproduction of Distributed Failures

On VMs today, everything runs on one or two machines. When something goes wrong a developer can SSH in, look at a single log file, and usually see the full picture in one place. After the migration, a failed order might involve a failed readiness probe on the API pod, a connection pool exhaustion on the RDS instance, a missing environment variable in a new deployment, and a network policy that accidentally blocks the worker from reaching the API — all visible in different places (pod logs, RDS CloudWatch metrics, Kubernetes events, CNI logs).

**Mitigation.**
Two things help significantly:

1. **Structured logging shipped to a central store.** All containers log JSON to stdout; a Fluent Bit DaemonSet ships logs to **Amazon CloudWatch Logs** (or an OpenSearch cluster). A developer can filter by `trace_id` or `order_id` and see the full timeline across every service involved, without touching individual pods.

2. **`docker compose` for local development.** A `docker-compose.yml` in the repo defines the same containers (API, worker, a local Postgres, and a MinIO container that emulates S3 for uploads) all wired with the same env var names used in production. This gives developers a reasonably faithful local environment and means many distributed issues can be reproduced without a cluster. It does not solve everything (node affinity, network policies, IAM) but it dramatically narrows the class of "only breaks in prod" problems.

---

## Summary Table

| Pain Point | Kubernetes Mechanism | Specific Control |
|---|---|---|
| Snowflake hosts / host drift | Immutable container images | Image pinned by digest in Deployment spec |
| Secrets in git / on disk | External secrets management | AWS Secrets Manager + External Secrets Operator |
| No rollback path | ReplicaSet history + rolling updates | `kubectl rollout undo` / readiness gating |
| Uploads on local disk | Shared object storage | S3 via `DATA_DIR` env var |
| Monolith restart = downtime | Multiple replicas + separate worker | Rolling update strategy + independent Deployments |
| **Harder: distributed debugging** | Centralized observability + local compose | CloudWatch Logs + docker compose dev env |