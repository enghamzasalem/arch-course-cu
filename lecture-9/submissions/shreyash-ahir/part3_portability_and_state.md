**part3\_portability\_and\_state**

1. Menu Uploads: Shared Storage Strategy: CityBite needs to store menu images so that every Pod can see them. We compared using a **Persistent Volume Claim (PVC)** via AWS EFS versus **Object Storage (S3)**.

|  |  |  |
| --- | --- | --- |
| **Strategy** | **Pros** | **Cons** |
| **PVC (AWS EFS)** | **Simple Migration:** The app just writes to a folder (/app/uploads). No code changes needed. | **Performance:** Network file systems can be slightly slower than local disks for high-frequency reads. |
| **Object Storage (S3)** | **Scalability & Cost:** Extremely cheap and built for billions of files. Easy to backup via versioning. | **Complexity:** Requires rewriting the Python code to use the boto3 library instead of standard file saving. |

**Decision:** We will use **PVC with AWS EFS**. It allows us to fix the "local disk" pain point immediately without refactoring the application code.

1. Secrets Management : Passwords and API keys for payment gateways must never be hardcoded or baked into the Docker image.

* **Storage:** We use **AWS Secrets Manager** as the "Source of Truth."
* **Injection:** We use the **External Secrets Operator** in Kubernetes. It automatically syncs secrets from AWS into a standard **Kubernetes Secret**.
* **Access:** The app reads these as Environment Variables. If we rotate a password in AWS, it updates in the cluster without a rebuild.

1. Database: Managed Postgres (RDS): We will keep the database **outside** the Kubernetes cluster (using AWS RDS).

* **Justification:** Databases are "heavy." Kubernetes is great at moving "light" apps around, but moving a 500GB database is risky. Keeping it on RDS gives us automated backups, easy patching, and high availability managed by AWS.
* **Connection:** The Pods receive a DATABASE\_URL env var. Since the DB is outside the cluster, we ensure the Kubernetes VPC (network) is "peered" with the RDS VPC.

1. Dev/Prod Parity : To ensure "it works on my machine" translates to "it works in production," developers run the app using **Docker Compose**.

* Local setup: Uses the same python:3.11-slim image.
* Local storage: Instead of EFS, Docker Compose mounts a **local folder** on the developer's laptop to the DATA\_DIR inside the container.
* This allows developers to test the exact same container behavior without needing a full cloud cluster.