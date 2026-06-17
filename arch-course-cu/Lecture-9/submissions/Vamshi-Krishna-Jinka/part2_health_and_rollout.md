# Part 2: Health, Rollout, and Failure — CityBite

## Overview

In Kubernetes, we use **health checks** and **controlled rollouts** to make deployments safe.
This helps CityBite avoid downtime and detect problems early.

---

## 1. Health Checks (Probes)

Kubernetes uses two types of probes:

### Liveness Probe (Is the app alive?)

* Purpose: Check if the container is still running correctly
* If it fails → Kubernetes **restarts the container**

**Configuration (example):**

* Type: HTTP
* Path: `/health/live`
* Port: `PORT` (e.g., 8080)
* Initial delay: 10 seconds
* Period: 10 seconds
* Failure threshold: 3

 If the API is stuck or crashes, it will be restarted automatically.

---

### Readiness Probe (Is the app ready to serve traffic?)

* Purpose: Check if the app can handle requests
* If it fails → Pod is **removed from Service (no traffic sent)**

**Configuration (example):**

* Type: HTTP
* Path: `/health/ready`
* Port: `PORT`
* Initial delay: 5 seconds
* Period: 5 seconds
* Failure threshold: 2

 This ensures users do not hit a pod that is still starting or having issues.

---

## 2. Rolling Update (v1.4.0 → v1.5.0)

When we deploy a new version of the API:

### Step-by-step:

1. A new image (`v1.5.0`) is pushed to the container registry
2. Kubernetes **updates the Deployment**
3. It creates new Pods with version `v1.5.0`
4. At the same time, old Pods (`v1.4.0`) are slowly removed

### Strategy:

* `maxUnavailable: 0` → no downtime
* `maxSurge: 1` → one extra pod allowed

### What happens if new Pods fail readiness?

* New Pods will **not receive traffic**
* Old Pods (v1.4.0) continue serving users
* Kubernetes will keep trying to start new Pods
* If failures continue, rollout will **pause or fail**

 This protects users from broken updates.

---

## 3. Failure Handling and Rollback

### Detecting a Bad Deployment

We can detect problems using:

* **Metrics** (e.g., high error rate, slow response time)
* **Logs** (errors in stdout logs)
* **Health checks** (readiness probe failures)

Example:

* After deploying v1.5.0, error rate increases
* Many Pods fail readiness

---

### Rolling Back

Kubernetes keeps the previous version (ReplicaSet).

To rollback:

```bash
kubectl rollout undo deployment/citybite-api
```

### What happens:

* Kubernetes stops using the bad version (v1.5.0)
* It brings back the previous version (v1.4.0)
* Traffic is again served by stable Pods

---

## Summary

* **Liveness probe** → restarts broken containers
* **Readiness probe** → controls traffic safely
* **Rolling updates** → zero-downtime deployments
* **Rollback** → quick recovery from failures

This setup makes CityBite deployments **safe, reliable, and easy to manage**.
