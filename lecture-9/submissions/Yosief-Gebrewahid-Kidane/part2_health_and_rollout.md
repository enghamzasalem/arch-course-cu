# Part 2 — Health, Rollout, and Failure (CityBite)

## 1. Overview

This section explains how the CityBite Order API ensures reliability in Kubernetes using health probes, rolling updates, and rollback mechanisms.

---

## 2. Health Probes

Kubernetes uses **liveness** and **readiness** probes to monitor application health and control traffic routing.

---

### 2.1 Liveness Probe

**Purpose:**  
Detect whether the application is still running correctly. If it is not, Kubernetes restarts the container.

**Example configuration:**
- Type: HTTP
- Endpoint: `/health/live`
- Port: `PORT`
- Initial delay: 10 seconds
- Period: 10 seconds
- Failure threshold: 3

**Behavior:**
- If the probe fails repeatedly, Kubernetes restarts the container automatically using the kubelet.

---

### 2.2 Readiness Probe

**Purpose:**  
Determine whether the application is ready to receive traffic.

**Example configuration:**
- Type: HTTP
- Endpoint: `/health/ready`
- Port: `PORT`
- Initial delay: 5 seconds
- Period: 5 seconds
- Failure threshold: 3

**Behavior:**
- If the probe fails, the pod is removed from the Service endpoints
- It continues running but receives no traffic until it becomes ready again

---

### 2.3 Key Difference

| Probe Type | Purpose | Failure Behavior |
|------------|---------|------------------|
| Liveness   | Ensures app is alive | Restart container |
| Readiness  | Ensures app can serve traffic | Remove from Service endpoints |

---

## 3. Rolling Updates

### 3.1 Deployment Scenario

CityBite updates the API from `v1.4.0` to `v1.5.0`.

---

### 3.2 Kubernetes Deployment Behavior

- The Deployment controller creates a new ReplicaSet for `v1.5.0`
- New pods are started gradually
- Old pods are scaled down incrementally
- Kubernetes ensures that only **ready pods receive traffic via the Service**

This enables **zero-downtime deployment**.

---

### 3.3 Failure During Rollout

If new pods fail readiness checks:
- They remain in a non-ready state
- They are not added to Service endpoints
- Old ReplicaSet continues serving traffic
- Rollout is automatically paused by Kubernetes

---

## 4. Incident Detection and Rollback

---

### 4.1 Detection Signals

A faulty deployment can be detected using:
- Increased HTTP 5xx error rates
- Failed readiness or liveness probes
- High latency or CPU spikes
- Logs collected from stdout

---

### 4.2 Rollback Strategy

Kubernetes supports rollback to a previous stable version.

**Example command:**
```bash id="k9r2lm"
kubectl rollout undo deployment citybite-api
---

### 4.3 Recovery Process

1. Monitoring detects anomalies
2. Deployment is identified as the cause
3. Rollback is triggered (manual or automated)
4. Previous ReplicaSet is reactivated
5. Traffic stabilizes via Service routing

