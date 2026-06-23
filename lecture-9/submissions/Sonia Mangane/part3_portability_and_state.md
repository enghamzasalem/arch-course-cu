
# Task 3.1: Portability, Data, and Pipeline

## 3.1 Menu Uploads: Storage Comparison
We choose **Object Storage (AWS S3)** over PVC.

| Strategy | Pros | Cons |
|:---|:---|:---|
| **S3 (Object Storage)** | High durability; native CDN support; infinite scale. | Requires refactoring code to use SDK instead of direct disk writes. |
| **PVC (EFS/EBS)** | File-system compatible (drop-in replacement). | Higher management overhead; potential I/O bottlenecks. |

## 3.2 Secrets and Database
* **Secrets:** Managed via **AWS Secrets Manager**, injected into K8s using the **External Secrets Operator**.
* **Database:** We will keep **Amazon RDS (Postgres)** outside the cluster to ensure data persistence is decoupled from the cluster lifecycle. Connection is managed via the `DATABASE_URL` environment variable.

## 3.3 Dev/Prod Parity
Developers use `docker-compose` locally. This simulates the K8s environment by:
1.  Using the same Dockerfile.
2.  Mounting a local folder to `DATA_DIR` to simulate the cloud storage.
3.  Spinning up a local Postgres container to match the production RDS schema.