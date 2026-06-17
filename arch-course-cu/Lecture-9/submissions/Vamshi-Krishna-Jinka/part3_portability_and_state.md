# Part 3: Portability and State — CityBite

## Overview

CityBite must run correctly in different environments:

* Developer laptop
* CI pipeline
* Production (Kubernetes on AWS EKS)

To achieve this, we handle **storage, secrets, database, and local development** carefully.

---

## 1. Menu Uploads (State Management)

We have two main options for storing menu images:

### Option 1: Persistent Volume (PVC + DATA_DIR)

* Use a **Kubernetes Persistent Volume (EFS in AWS)**
* Mount it inside the container at a fixed path (e.g., `/var/data`)
* Use `DATA_DIR` environment variable to store files

**Pros:**

* Simple to use (acts like a normal folder)
* Easy to integrate with existing code

**Cons:**

* More expensive for large storage
* Harder to scale globally (multi-region)

---

### Option 2: Object Storage (Amazon S3)

* Store images in **S3 bucket**
* API uploads files directly to S3

**Pros:**

* Very scalable and durable
* Built-in backup and replication
* Lower cost for large data

**Cons:**

* Slightly more complex (need SDK, credentials)
* Requires network calls (not local disk)

---

 For CityBite, **S3 is better** because:

* Many restaurants upload images
* Data grows over time
* We need durability and scalability

---

## 2. Secrets Management

Sensitive data must **not be stored in the container image**.

### Where secrets are stored:

* **Kubernetes Secrets** (basic level)
* Integrated with **AWS Secrets Manager** (recommended)

### Examples of secrets:

* Database password
* Payment API keys

### How they are used:

* Injected into containers as **environment variables**
* Example:

  * `DATABASE_URL`
  * `PAYMENT_API_KEY`

 This keeps secrets secure and separate from code.

---

## 3. Database Design

### Choice: Managed PostgreSQL (outside Kubernetes)

* Use **AWS RDS (PostgreSQL)**
* Database runs outside the cluster

**Why?**

* Easier backups and maintenance
* High availability (multi-AZ)
* No need to manage DB inside Kubernetes

---

### Connection from Pods

* Use `DATABASE_URL` environment variable
* Example:

```
postgresql://user:password@db-host:5432/citybite
```

* Inject this using **Kubernetes Secrets**

 This follows the same pattern as in 

---

## 4. Dev / Prod Parity

Developers should run the system in a similar way to production.

### Local Setup (Docker Compose)

* Run API container locally
* Run a local database (Postgres or SQLite)
* Mount a volume for uploads

Example:

* `DATA_DIR=./data` (local folder)
* Volume mapping → `./data:/var/data`

 This follows the same idea as 
→ same environment variables, same paths

---

### Benefits:

* Same configuration style (env variables)
* Easy to test locally
* Fewer surprises in production

---

## Summary

* Use **S3 for menu uploads** (scalable and reliable)
* Store secrets in **Kubernetes Secrets + AWS Secrets Manager**
* Use **managed PostgreSQL (RDS)** outside the cluster
* Maintain **dev/prod parity** using Docker Compose and environment variables

This design ensures CityBite is **portable, secure, and consistent** across all environments.
