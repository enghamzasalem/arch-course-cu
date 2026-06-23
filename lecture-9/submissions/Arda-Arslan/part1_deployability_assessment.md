# Task 1.1 - Deployability Assessment

CityBite currently runs as a monolith on long-lived VMs with manual SSH deployments, per-host configuration, local disk storage for uploads, and downtime during restarts.

## Deployability risks and mitigations

### 1. Host drift between VMs
The current setup uses long-lived VMs that may differ over time. This makes deployments inconsistent, because the same release may behave differently depending on the VM.

**Mitigation:** Package the application as an immutable container image and deploy that exact image in Kubernetes. The Deployment should reference a specific image tag or digest, so every pod runs the same build.

### 2. Manual SSH deployment is slow and error-prone
Today, deployment depends on manual SSH scripts. This increases human error, slows release throughput, and makes deployments harder during busy periods such as dinner spikes.

**Mitigation:** Build images in CI and deploy them through Kubernetes manifests instead of manual SSH steps. This makes deployments more repeatable and reduces human error.

### 3. Configuration is edited separately on each VM
CityBite currently keeps `.env` files on disk per VM. This creates unclear ownership of configuration and makes it easy for environments to drift apart.

**Mitigation:** Move runtime configuration to environment variables managed by Kubernetes ConfigMaps and Secrets. Values such as `PORT`, `DATABASE_URL`, `LOG_LEVEL`, and `DATA_DIR` are injected by the platform.

### 4. Menu uploads are coupled to local VM disk
Menu JPEGs are stored on local VM disk under `/var/citybite/uploads`. This is a portability problem because containers should be disposable, and local disk data may be lost or unavailable after rescheduling.

**Mitigation:** Mount a writable volume in Kubernetes and inject the path via `DATA_DIR`. Details are covered in Task 3.1.

### 5. Restarting the monolith causes partial downtime
Restarting the monolith causes minutes of partial downtime. This is a major deployability issue because users may be affected during every release.

**Mitigation:** Use a Kubernetes Deployment with rolling updates and readiness probes. New pods should become ready before old pods are removed from service, so traffic only goes to healthy instances.

## One thing that becomes harder after the move

After moving to Kubernetes, troubleshooting can become harder because the system is more distributed than a single VM. Instead of checking one machine, engineers may need to inspect several pods and logs.

**Mitigation:** Run similar containers locally (e.g. with Docker Compose) and use centralized stdout logging and simple health endpoints to make debugging easier.