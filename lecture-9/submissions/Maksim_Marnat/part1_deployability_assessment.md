# Part 1.1 — Deployability assessment (CityBite → EKS)

**Target stack:** AWS **EKS** (Kubernetes), **ECR** images, **RDS PostgreSQL**, **S3** for menu JPEGs, **ALB Ingress Controller**. Baseline per assignment: monolith on long-lived VMs, SSH deploys, per-host `.env`, uploads on VM disk.

## Deployability risks and mitigations

| # | Risk (baseline) | Mitigation (K8s + containers) |
|---|-----------------|--------------------------------|
| 1 | **Host drift / snowflake VMs** — packages and file layouts differ; reproducing prod on a new host is guesswork. | **Immutable image digest** pinned in `Deployment` (same artifact everywhere); node pool is generic; config only via env/ConfigMap/Secret, not baked into AMIs. |
| 2 | **Manual SSH deploys** — slow, error-prone, no audited pipeline; rollback means “re-run old script and hope”. | **CI pipeline** (e.g. GitHub Actions) builds and pushes `:git-sha` to **ECR**; release applies a manifest with that digest; rollback = **repoint to previous digest** or `kubectl rollout undo`. |
| 3 | **Secrets in repo or on-disk `.env`** — rotation is painful; blast radius if a host is compromised. | **No secrets in image layers**; runtime injection via **Kubernetes Secret** synced from **AWS Secrets Manager** (e.g. External Secrets Operator); **IRSA** for S3/RDS access where possible. |
| 4 | **Stateful paths on VM disk** (`/var/citybite/uploads`) — tied to a machine; backups and scaling out are manual. | **S3** for menu blobs; app uses **presigned URLs** or SDK with IAM role for service account; no reliance on node-local disk for user content. |
| 5 | **Deploy = restart monolith → minutes of partial downtime** — no gradual traffic shift, no signal whether the new process is ready. | **Rolling update** `maxUnavailable`/`maxSurge`; **readiness** gates traffic until DB and dependencies are OK; optional **PDB** so one node drain does not kill all replicas during dinner spike. |
| 6 | **Unclear config ownership** — ops edited files on hosts; “what runs in prod?” was implicit. | **GitOps or versioned manifests** in repo; **ConfigMaps** for non-secret tuning (`LOG_LEVEL`); single **Deployment** spec describes desired state; audit trail via PR + CI. |

## What becomes harder — and how we address it

**Harder:** End-to-end failures now span **ingress → Service → Pod → RDS/S3**; a bug that only appears under load or with real IAM is **less reproducible** on a laptop than a single VM with SSH.

**Mitigation:** **Structured JSON logs to stdout** (same as lecture examples) → CloudWatch; **staging EKS** namespace with same chart and smaller nodes; **integration tests in CI** against docker compose (Postgres + LocalStack/MinIO); runbooks for `kubectl describe pod`, **rollout undo**, and comparing **ECR image digest** to last known good.
