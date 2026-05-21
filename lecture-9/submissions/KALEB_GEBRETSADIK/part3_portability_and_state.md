# Part 3: Portability, Data, and Pipeline

## Task 3.1: Portability and State

### 1. Menu Uploads (Object S3 vs Kubernetes PVC)

**Architectural Decision:** We will manage CityBite's menu uploads strictly via **External Object Storage (Amazon S3)** rather than tracking explicit Kubernetes Persistent Volume Claims (PVCs).

**Pros (Amazon S3 Advantages):**
*   **Infinite Elasticity & Direct Serving:** Amazon S3 abstracts away all underlying disk capacity caps. Crucially, the uploaded restaurant JPEGs can be securely served directly from the remote S3 bucket (or via an attached CDN like CloudFront) straight to the mobile client device, radically eliminating unnecessary routing processing power away from the main application pods.
*   **Complete Stateless Isolation:** EKS application pods become entirely stateless and ephemeral. If we had used typical `ReadWriteOnce` PVC blocks, dynamically shifting a pod forcefully across different Availability Zones during an incident can occasionally cause nasty storage-attachment deadlocks. S3 bypasses node-affinity storage risks perfectly.

**Con (Amazon S3 Disadvantage):**
*   **Code Complexity Constraints:** Adopting external object storage natively mandates refactoring and rewriting legacy baseline codebase mechanisms. Rather than simply writing IO streams smoothly to standard disk paths (e.g. `DATA_DIR=/app/uploads`), developers must import heavy AWS SDK clients like `boto3`, forcing application layers to handle complex network timeouts and strict authentication handling manually. 

---

### 2. Secrets Management Configuration

Because baking strings directly into the container image layer heavily breaks security compliance and locks configurations fatally to previous builds, we implement an **External Secret + Native Kubernetes** projection combination.

*   **Mapping Strategy:** Highly sensitive infrastructure items like Database passwords and Payment Gateway API Keys natively reside securely within a cloud-managed provider like **AWS Secrets Manager**. We then deploy an agent (like the *External Secrets Operator*) operating heavily encrypted inside the EKS cluster. This agent continually fetches target variables from AWS natively and generates them transparently as standard decoupled Kubernetes `Secret` objects. 
*   **Pod Runtime Mapping:** The target Application deployment manifest seamlessly attaches the Kube `Secret` resource into the Pod execution layer smoothly bridging the values explicitly as environment variables (e.g. `DATABASE_URL` and `PAYMENT_API_KEY`). The application never relies explicitly on IAM assumptions nor queries AWS Secrets Manager manually; maintaining optimal multi-cloud application portability.

---

### 3. Managed Database Topology

**Architectural Decision:** We strictly isolate the primary Managed PostgreSQL Database continuously **OUTSIDE** of the Kubernetes perimeter, hosted actively on **Amazon RDS**.

*   **Justification:** Databases are inherently heavy stateful applications. While Kubernetes supports databases through complex `StatefulSet` topologies, attempting to manually manage disk replication lag, multi-AZ high availability constraints, and complex disaster recovery WAL logs inside Kubernetes is exceptionally delicate operations labor. Storing the DB explicitly in Amazon RDS shifts massive disaster recovery persistence, automated minor-version patching, and automated snapshot backups reliably off the Devops plate.
*   **Pod Connectivity:** The EKS Application pods cleanly remain totally unaware of this macro-provider structural decision. To them, the DB natively acts as an arbitrary TCP service string fetched completely off their exact `$DATABASE_URL` environment injection pointing explicitly to an Amazon RDS FQDN string (e.g., `postgresql://citybite:secret@citybite-production.cluster-aws.us-east-1.rds.amazonaws.com5432/main_db`).

---

### 4. Development and Production Parity

To actively ensure precise "12-factor Dev/Prod Parity", engineers will replicate the immutable OS dependencies natively without clashing across diverse hardware by strictly mandating identical Dockerfile environments via **Docker Compose** on local laptops. Instead of relying on production-level managed layers (AWS RDS or S3), developers override the environment variables natively in the localized `.env.local` hook connected directly to the compose schema. They dynamically spin up a lightweight, deeply native simulated `postgres:15-alpine` container acting perfectly identically to Amazon RDS schema, while transparently simulating the exact `S3 / DATA_DIR` requirement natively by configuring an ephemeral mock storage system like the `Minio Server` container or hooking an isolated local anonymous volume straight back mapping explicitly back to the `S3_BUCKET_NAME` context. 
