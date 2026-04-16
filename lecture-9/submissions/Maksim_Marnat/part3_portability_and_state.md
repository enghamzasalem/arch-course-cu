# Part 3.1 — Portability, data, secrets

**Cloud:** AWS only (`AWS_REGION`, EKS, ECR, RDS, S3).

## Menu uploads: **S3** (not PVC)

Choice for CityBite: **S3** for menu JPEGs; **`DATA_DIR`** remains for **local/docker compose** parity when S3 is mocked or disabled.

| | **Pros (CityBite)** | **Cons (CityBite)** |
|--|---------------------|---------------------|
| **S3** | **Durability & backup:** object versioning + cross-region replication fit partner-uploaded menus without per-node backup scripts. **Horizontal scale:** API pods stay stateless; dinner spikes add replicas without “which node has the files?” | **Complexity:** IAM (IRSA), presigned URLs or server-side upload policy; **cost** for egress if apps pull full images repeatedly without CloudFront. |
| **PVC + `DATA_DIR`** | **Simpler app path:** POSIX path like today’s VM disk; **predictable** latency for small files on same AZ. | **Ops burden:** EBS snapshots, **zone affinity**, resize; **multi-AZ** failover for stateful volumes is harder than S3 for blob workload. |

**Conclusion:** For **regional many-restaurant JPEG storage**, S3 wins; PVC is reserved only if compliance mandates on-cluster disk (not assumed here).

## Secrets

- **DB password / `DATABASE_URL`:** AWS **Secrets Manager** → **External Secrets Operator** → Kubernetes **Secret** → env in Pod spec.  
- **Payment API keys:** same pattern, separate Secret key.  
- **Never** in `docker build` args or image layers; CI uses OIDC to AWS for deploy, not long-lived keys in repo.

## Database

**RDS PostgreSQL** stays **outside** the cluster (managed backups, Multi-AZ). Pods connect via **`DATABASE_URL`** from Secret; security group allows **only** EKS node/pod CIDRs to **5432**.

## Dev / prod parity

Developers run **`docker compose`**: `order-api` + `postgres` + **MinIO** (S3 API) + volume for optional local `DATA_DIR` fallback; same **`PORT`**, **`LOG_LEVEL`**, **`DATABASE_URL`** shape as prod; `AWS_REGION` set for SDK; MinIO bucket emulates `MENU_S3_BUCKET`. CI runs **lint + tests** against compose services so “works on my machine” matches **container contract** before **ECR** push.
