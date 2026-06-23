# Task 2.2 - Health, Rollout, and Failure

## Liveness and readiness probes

For the **CityBite Order API**, I would use simple HTTP health endpoints.

- **Liveness probe:** `GET /health`
- **Readiness probe:** `GET /ready`

The **liveness probe** checks whether the API process is still running correctly. If this probe fails several times, Kubernetes restarts the container.

The **readiness probe** checks whether the pod is ready to receive traffic. A pod may be alive but still not ready, for example if it is still starting or cannot connect to the database. If readiness fails, the pod stays out of the Service and does not receive user requests. This matches the lecture idea that readiness controls traffic, while liveness controls restarts. 

A plausible configuration is:

- **Liveness:** initial delay 15 seconds, period 10 seconds, failure threshold 3
- **Readiness:** initial delay 5 seconds, period 5 seconds, failure threshold 3

This allows the API some startup time while still detecting unhealthy containers reasonably quickly.

## Rolling update from v1.4.0 to v1.5.0

During a rolling update from image **v1.4.0** to **v1.5.0**, Kubernetes creates new pods with the new image while the old pods are still running. The Service continues sending traffic to the old ready pods until the new pods pass their readiness probe. After the new pods become ready, traffic starts moving to them, and the old pods are removed gradually. This reduces downtime during deployment. 

If the new **v1.5.0** pods fail readiness, they do not receive traffic. In that case, the old **v1.4.0** pods continue serving users, so the rollout does not fully replace the working version.

## Detecting and rolling back a bad deploy

A bad deploy can be detected through failed readiness probes, higher error rates, and container logs after the rollout starts. If the new version shows problems, I would roll back to the previous ReplicaSet using `kubectl rollout undo deployment/citybite-order-api`. This returns the deployment to the last working version and is a simple way to recover from a failed release.