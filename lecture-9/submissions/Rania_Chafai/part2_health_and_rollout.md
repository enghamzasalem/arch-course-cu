# Part 2 — Health Checks and Rollout Strategy for CityBite

## 1. Overview

In the Kubernetes-based deployment of CityBite, health checks and rollout strategies ensure high availability, reliability, and safe deployments.

Kubernetes continuously monitors container health and manages deployments automatically, reducing operational risk and improving system stability.

---

## 2. Health Probes Overview

Kubernetes uses three types of probes:

| Probe         | Purpose                                         | Action on Failure   |
| ------------- | ----------------------------------------------- | ------------------- |
| **Liveness**  | Checks if container is still running correctly  | Restart container   |
| **Readiness** | Checks if container is ready to receive traffic | Remove from Service |
| **Startup**   | Handles slow application startup                | Delays other probes |

These probes ensure that only healthy and ready containers serve user requests.

---

## 3. Liveness Probe

### Purpose

The liveness probe detects failures such as crashes or deadlocks. If it fails, Kubernetes automatically restarts the container.

### Example (API container)

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 30
  timeoutSeconds: 3
  failureThreshold: 3
```

### Explanation

* `/health` verifies that the application is alive
* Failure triggers container restart
* Enables automatic recovery

---

## 4. Readiness Probe

### Purpose

The readiness probe determines if the container is ready to receive traffic. If it fails, the pod is removed from the load balancer.

### Example (API container)

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

### Explanation

* Prevents traffic to unready containers
* Ensures smooth deployments
* Improves user experience

---

## 5. Startup Probe

### Purpose

The startup probe is used for containers that take longer to start. It disables liveness and readiness checks until the application is fully initialized.

### Example

```yaml
startupProbe:
  httpGet:
    path: /health
    port: 3000
  failureThreshold: 30
  periodSeconds: 2
```

---

## 6. Health Strategy per Service

| Service  | Liveness      | Readiness   |
| -------- | ------------- | ----------- |
| Frontend | HTTP `/`      | HTTP `/`    |
| API      | `/health`     | `/ready`    |
| Redis    | TCP 6379      | TCP 6379    |
| Worker   | Process check | Not exposed |

---

## 7. Rolling Update Strategy

Kubernetes uses rolling updates to deploy new versions without downtime.

### Example Configuration

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1
```

### Explanation

* Only one pod can be unavailable at a time
* A new pod is created before removing an old one
* Ensures continuous service availability

---

## 8. Deployment Workflow

1. Developer pushes code
2. CI/CD builds container image
3. Image is pushed to Amazon ECR
4. Kubernetes updates the deployment
5. New pods are created
6. Readiness probe validates pods
7. Traffic is gradually shifted
8. Old pods are removed

This ensures zero-downtime deployment.

---

## 9. Rollback Strategy

If a deployment fails, Kubernetes allows fast rollback.

### Example

```bash
kubectl rollout undo deployment citybite-api
```

### Benefits

* Quick recovery
* Reduced downtime
* Safer releases

---

## 10. Failure Handling

Kubernetes provides self-healing:

* Crashed containers are restarted
* Unhealthy pods are removed from service
* Pods are rescheduled if a node fails

---

## 11. Summary

This strategy improves deployability by:

* ensuring only healthy containers receive traffic
* enabling safe and gradual deployments
* allowing fast rollback
* reducing downtime
* supporting continuous delivery

Kubernetes provides a robust and automated system to manage application health and deployment lifecycle.
