# Task 3.1 - Portability and State

## Menu uploads

For CityBite, I choose **PVC + `DATA_DIR`** for menu uploads.

**Pros:**
1. It keeps the application code portable, because the upload path is provided through `DATA_DIR` instead of being hardcoded.
2. It is a simpler design for CityBite’s current size, because the API can write uploaded menu images to a mounted directory without adding another storage service.

**Cons:**
1. Backup and disaster recovery need extra setup, because a volume alone is not enough for safe long-term storage.
2. It is less flexible than object storage if the system grows and needs easier sharing across multiple services or regions.

This choice is consistent with the earlier design, where menu uploads move from VM disk to Kubernetes storage and the application writes to a configurable path.

## Secrets

Secrets such as payment API keys and database passwords should not be stored in the image layer or committed to Git. In the target architecture, they should be stored in **AWS Secrets Manager** and exposed to the application through **Kubernetes Secrets**. This keeps sensitive values outside the container image and allows them to be managed separately from the application code.

## Database

The PostgreSQL database should remain **outside the cluster** as a managed service. This is a better fit for CityBite than running the database inside Kubernetes, because the application layer can stay easier to replace while the database is managed separately. The API pods connect to the database through the `DATABASE_URL` environment variable, which is injected at runtime.

## Dev/prod parity

To keep development close to production, developers should run similar containers locally with **docker compose**. A local setup can include the API container, a local PostgreSQL container, and a mounted local volume for `DATA_DIR`. This way, developers use the same environment-variable style configuration and the same container process model as in the cluster, while still being able to test uploads and database access on a laptop.