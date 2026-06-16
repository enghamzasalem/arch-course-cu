# Part 3: Portability and State — CityBite

---

## 3.1 Menu Uploads: PVC + DATA_DIR vs Object Storage (S3)

CityBite's menu images are uploaded by restaurant partners through the tablet app and served back to customers browsing the menu. The storage layer for these files must be shared across all API pods, survive pod restarts, and be reachable from the local development environment using the same application code path (`DATA_DIR`).

### Option A — PVC backed by Amazon EFS (current design choice)

A Kubernetes PersistentVolumeClaim with `accessModes: ReadWriteMany` is provisioned against the EFS CSI driver. Every API pod mounts it at the path defined by `DATA_DIR` (`/mnt/uploads`). The application code reads and writes files using ordinary filesystem calls — no SDK, no HTTP client, no presigned URL logic.

**Pros:**
- Zero application code change from the monolith. The existing file-write path (`open(DATA_DIR / filename, "wb")`) works identically in a container as it did on the VM. Portability to local dev is trivial: a Docker named volume mounted at the same path produces identical behaviour.
- EFS replicates data across multiple Availability Zones within the region by default, so durability is built in without any application-level backup logic.

**Cons:**
- EFS throughput pricing is based on data transferred and storage used, and EFS provisioned throughput can become expensive at scale if many pods are reading large JPEG files concurrently. For CityBite's current traffic this is unlikely to be an issue, but at high read volume a CDN in front of EFS would be needed to avoid both cost and latency problems.
- The EFS volume is regional. If CityBite ever needs to operate in multiple AWS regions (e.g. for a second city in a different geography), images written to one region's EFS are not automatically available in the other. Cross-region replication requires additional configuration.

### Option B — Amazon S3 (alternative)

Menu images are uploaded to an S3 bucket. The application uses the `boto3` SDK to `put_object` on upload and generates a presigned URL (or CloudFront URL) on read. `DATA_DIR` is either retired or repurposed as a local temp directory for upload staging.

**Pros:**
- S3 is designed for high-throughput, low-latency object reads at any scale. Pairing it with a CloudFront distribution makes menu images available with low latency globally, which would matter if CityBite expands beyond a single city.
- S3 storage is significantly cheaper per GB than EFS for infrequently written, frequently read objects (menu images change rarely after upload). S3 also provides eleven nines of durability natively.

**Cons:**
- Requires code changes to the upload and serve paths (SDK calls, presigned URL generation, IAM role configuration). The application can no longer treat storage as a filesystem, which increases the cost of local development parity — a MinIO container must stand in for S3, and developers must configure `AWS_ENDPOINT_URL` to point at it.
- Presigned URL expiry adds a class of bugs (expired links cached by the mobile app) that do not exist in the filesystem model.

### Decision

EFS (Option A) is retained for the current architecture. CityBite's scale does not yet justify the added code complexity of S3 integration, and the filesystem abstraction via `DATA_DIR` is what makes the container portable across local, CI, and production without code changes. If CityBite grows to operate across multiple regions or requires global CDN delivery of menu images, migrating to S3 + CloudFront at that point is a well-understood path.

---

## 3.2 Secrets Management

No secret value is baked into a container image. The image contains only code. All credentials are injected at pod startup by the Kubernetes platform.

### Architecture

```
AWS Secrets Manager
        │
        │  ASCP (AWS Secrets and Configuration Provider)
        │  syncs on pod creation, rotates on schedule
        ▼
Kubernetes Secret  (citybite-prod-secrets, namespace: citybite-prod)
        │
        │  env.valueFrom.secretKeyRef
        ▼
Pod environment variables
  DATABASE_URL=postgresql://…
  PAYMENT_API_KEY=sk_live_…
  SMTP_KEY=…
  SENTRY_DSN=…
```

**AWS Secrets Manager** is the source of truth for all production secrets. It supports automatic rotation (e.g. RDS credential rotation via a Lambda rotator), versioning, and fine-grained IAM policies so that only the `citybite-api` service account can read the secrets it needs.

The **AWS Secrets and Configuration Provider (ASCP)**, installed as a Kubernetes CSI driver, watches the pod spec for `SecretProviderClass` references and materialises the Secrets Manager values into a native Kubernetes `Secret` object at pod startup. The pod then consumes the secret as environment variables via `env.valueFrom.secretKeyRef`. If Secrets Manager rotates a credential, a pod restart (e.g. on the next rollout) picks up the new value automatically.

**Non-sensitive configuration** (`LOG_LEVEL`, `PORT`, `DATA_DIR`, `AWS_REGION`) lives in a ConfigMap and is injected via `envFrom`. ConfigMaps are not encrypted at rest by default; they should never contain secret material.

**Local development:** developers use a `.env` file that is listed in `.gitignore`. The `docker-compose.yml` loads it via `env_file: .env`. The `.env` file contains development-only credentials (a local Postgres password, a Stripe test key). It never contains production values. This pattern is explicitly documented in `CONTRIBUTING.md` with a warning that production secrets are managed exclusively through AWS Secrets Manager.

---

## 3.3 Database: Managed Postgres Outside the Cluster

### Why managed RDS, not an in-cluster Postgres

Running Postgres inside Kubernetes as a StatefulSet is technically possible but operationally expensive. It requires manual management of storage provisioning (EBS volumes per replica), replication lag monitoring, failover testing, and WAL archiving for point-in-time recovery. Amazon RDS Multi-AZ handles all of this as a managed service: automated failover within ~60 seconds, automated daily snapshots with 35-day retention, and minor version patching with a configurable maintenance window. The engineering effort saved by not operating Postgres in-cluster is better spent on product features.

The database is deliberately placed **outside** the EKS cluster, in the same AWS VPC, connected via a private subnet. No public endpoint is exposed. The RDS security group allows inbound TCP 5432 only from the EKS node security group.

### Connection from pods

`DATABASE_URL` is injected into every API and worker pod as a Kubernetes Secret (sourced from AWS Secrets Manager as described in §3.2). The value takes the form:

```
postgresql://citybite_app:REDACTED@citybite-prod.cluster-abc123.eu-central-1.rds.amazonaws.com:5432/citybite
```

The application uses SQLAlchemy's async engine with a connection pool (`pool_size=5`, `max_overflow=10`). The pool is initialised at Uvicorn startup and tested during the readiness probe (`SELECT 1`). If RDS performs an automated failover, the DNS endpoint (`*.rds.amazonaws.com`) is updated to point at the new primary within ~60 seconds; SQLAlchemy's connection pool will reconnect automatically on the next query after the DNS TTL expires.

### Local dev

The `docker-compose.yml` includes a Postgres 16 service:

```yaml
db:
  image: postgres:16-alpine
  environment:
    POSTGRES_DB: citybite_dev
    POSTGRES_USER: citybite_app
    POSTGRES_PASSWORD: devpassword
  volumes:
    - pgdata:/var/lib/postgresql/data
```

`DATABASE_URL` in the developer's `.env` points at this local container. The schema is kept identical to production via Alembic migrations that run in both environments.

---

## 3.4 Dev/Prod Parity

Developers run the full CityBite stack locally using `docker compose up`. The compose file defines four services: `api` (the same `citybite-api` image built from the local Dockerfile), `worker` (the same image with a different `command`), `db` (Postgres 16 Alpine), and `uploads` (a named volume mounted at `/mnt/uploads` inside both the `api` and `worker` containers). The `api` service sets `DATA_DIR=/mnt/uploads`, `PORT=8080`, `DATABASE_URL=postgresql://citybite_app:devpassword@db:5432/citybite_dev`, and `LOG_LEVEL=DEBUG` — the same variable names used in production, pointing at local containers instead of AWS services. This means the application binary is tested locally under conditions that are structurally identical to the cluster: the same image, the same environment variable contract, the same filesystem mount path for uploads. The only differences are the values of those variables (local Postgres vs RDS, named volume vs EFS) and the absence of the Kubernetes networking layer. Because the differences are purely in injected configuration and not in code or image content, a bug that passes local testing is very unlikely to be caused by a configuration-structural mismatch — which was the primary source of environment-specific bugs in the old VM model.
