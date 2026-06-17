# Part 3.1 - Portability and State

## Menu uploads

For CityBite, I choose **Object Storage (S3)** for menu uploads.

**Pros:**
1. It allows all pods to access the same images without extra replication, because S3 is a shared storage layer.
2. It provides built-in durability and backup, which reduces the risk of losing customer menu images during a cluster failure.

**Cons:**
1. The application code needs to use the S3 SDK instead of plain file writes, which adds a small development dependency.
2. It introduces slightly higher latency for each upload and fetch compared to a local volume.

This choice is consistent with the goal of keeping the API stateless, because menu images are stored outside the pod's ephemeral disk.

## Secrets

Secrets such as payment API keys and database passwords should not be stored in the image layer or committed to Git. In the target architecture, they should be stored in **AWS Secrets Manager** and exposed to the application through **Kubernetes Secrets**. This keeps sensitive values outside the container image and allows them to be managed separately from the application code.

## Database

The PostgreSQL database should remain **outside the cluster** as a managed service. This is a better fit for CityBite than running the database inside Kubernetes, because the application layer can stay easier to replace while the database is managed separately. The API pods connect to the database through the `DATABASE_URL` environment variable, which is injected at runtime.

## Dev/prod parity

To keep development close to production, developers should run similar containers locally with **docker compose**. A local setup can include the API container, a local PostgreSQL container, and a local S3-compatible service (e.g., MinIO) for `DATA_DIR`. This way, developers use the same environment-variable style configuration and the same container process model as in the cluster, while still being able to test uploads and database access on a laptop.