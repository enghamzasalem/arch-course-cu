## Part 3: Portability, Data, and Pipeline

### 3.1 Portability and State

This section details how CityBite manages configuration and persistent data across environments, ensuring that the application remains portable from a developer's laptop to the production cluster.

**1. Menu Uploads: Storage Strategy**
To replace the legacy approach of storing JPEGs on a local VM disk, we transition to an external storage provider to maintain container ephemerality.

| Option | Pros | Cons |
| :--- | :--- | :--- |
| **Object Storage (AWS S3)** | Highly scalable; built-in redundancy; offloads web server traffic via CDNs. | Requires SDK integration; slightly more complex local development setup. |
| **Persistent Volume Claim (PVC)** | Minimal code changes; acts like a standard file system. | Harder to scale across multiple regions; requires managing storage classes and backups. |

**Decision**: CityBite will use **AWS S3** for menu uploads. This aligns with the `DATA_DIR` abstraction, where the application writes to a path that the runtime contract maps to an S3 bucket in production.

**2. Secrets Management**
Sensitive data such as `DATABASE_URL` and payment API keys will **never** be stored in the container image layer or Git history.
* **Production**: Secrets are stored in **AWS Secrets Manager** and injected into Kubernetes as environment variables using a CSI driver or an External Secrets Operator.
* **Security**: This ensures that even if a developer has access to the container image, they do not have access to production credentials.

**3. Database Strategy**
CityBite will continue to use a **Managed PostgreSQL (Amazon RDS)** instance located outside the Kubernetes cluster.
* **Connection**: Pods connect via the `DATABASE_URL` environment variable.
* **Rationale**: Keeping the database external simplifies cluster management, leverages AWS's automated patching/backups, and prevents database performance from being impacted by application pod CPU spikes.

**4. Dev/Prod Parity**
To ensure developers can replicate the production environment locally:
* Developers use **Docker Compose** to run the API and Worker containers.
* A local **PostgreSQL container** is used for the database.
* For menu uploads, a **local volume mount** is mapped to the `DATA_DIR`, simulating the persistence required without needing a live S3 connection during offline development.

---

### 3.2 Delivery Sequence (Logic Summary)

The delivery pipeline ensures that every change is verified before reaching production.

1.  **Commit**: A developer pushes code to GitHub.
2.  **CI Build**: GitHub Actions triggers a build, runs tests, and packages the application into a container image tagged with the `git-sha`.
3.  **Registry**: The image is pushed to **Amazon ECR**.
4.  **Deploy**: The CI runner updates the Kubernetes Deployment manifest to the new image tag.
5.  **Validation**: The Kubernetes Control Plane pulls the image and initiates a rolling update.
6.  **Rollback Branch**: If the **Readiness Probe** fails (e.g., the container crashes on start), the cluster stops the rollout, keeping the previous version of the pods active to prevent service interruption.