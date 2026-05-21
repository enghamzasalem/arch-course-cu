# Part 1: Deployability and Target Architecture

## Task 1.1: Deployability Assessment

### Baseline Context
Currently, CityBite operates a monolith running on long-lived VMs. Deployments are handled via manual SSH scripts, configuration is managed by manually editing `.env` files per host, menu uploads are written straight to `/var/citybite/uploads` on the local VM disk attached to the specific host, and restarting the monolith takes minutes, leading to tangible downtime.

### 1. Deployability Risks and Kubernetes Mitigations

**Risk 1: Host Drift and "Snowflake" Servers**
*   **Baseline Pain:** Manual SSH deployments and unrecorded OS updates gradually cause every VM to diverge in configuration. A library version installed on Server A might be missing on Server B, leading to unpredictable "works on my machine" failures.
*   **K8s/Container Mitigation:** **Immutable Container Images.** We will build a single Docker image in CI containing the exact runtime dependencies. This exact image digest (SHA-256) will be pinned in the Kubernetes `Deployment` manifest and executed identically across all EKS worker nodes, guaranteeing absolute environment parity.

**Risk 2: Downtime During Restarts and Spikes**
*   **Baseline Pain:** Replacing the application requires stopping the old process and starting the new one, causing dropped connections and minutes of downtime—highly detrimental if a deploy must happen during the "evening dinner spike."
*   **K8s/Container Mitigation:** **K8s RollingUpdates and Probes.** Using a Kubernetes `Deployment` configured with a `RollingUpdate` strategy, EKS will provision new pods running the new version in the background. It will actively poll the new pods' `ReadinessProbes`; only when the new pods report as fully healthy will traffic be routed to them, safely terminating the old pods with zero downtime.

**Risk 3: Configuration Drift and Manual Secrets Management**
*   **Baseline Pain:** Relying on `.env` files sitting on local hard drives requires operators to manually SSH into multiple servers to rotate a password, frequently leaving secrets exposed in bash history profiles.
*   **K8s/Container Mitigation:** **Decoupled ConfigMaps and Secrets.** All configurations (like `AWS_REGION=us-east-1` or `LOG_LEVEL=INFO`) will be managed via Kubernetes `ConfigMaps`. Sensitive operational strings like `DATABASE_URL` will be securely injected using Kubernetes `Secrets` directly into the pod environment variables at runtime, shielding developers from raw infrastructure access and removing `.env` files from compute nodes.

**Risk 4: Tightly Coupled State (Local Disk Uploads)**
*   **Baseline Pain:** Storing menu JPEGs in `/var/citybite/uploads` tightly binds the application scale to a specific host. If the VM dies, the images are lost. If the app tries scaling horizontally to a second node, the new node's load balancer cannot access the menu images on the original server's path.
*   **K8s/Container Mitigation:** **Stateless Pods with External Object Storage.** The new pods will be completely stateless (optionally enforcing a read-only root filesystem for security). The backend code utilizing the `DATA_DIR` context will be rewritten to stream uploads directly via AWS SDK to an **Amazon S3 Bucket**, fully detaching persistence layers from the application compute.

**Risk 5: Slow and High-Risk Rollbacks**
*   **Baseline Pain:** If a bad code release breaks production, an operator must quickly figure out how to clone a previous Git commit, rebuild the package, and SSH rerun deployment scripts in a panic.
*   **K8s/Container Mitigation:** **Declarative Rollbacks (`kubectl rollout undo`).** Kubernetes natively tracks the history of `ReplicaSets`. Rolling back a critical failure requires a single command to scale the previous known-good deployment back up to 100%, entirely circumventing manual CI/rebuild steps in an emergency.

---

### 2. Trade-offs: What Becomes Harder?

**What is harder?** **Local Reproduction and Distributed Debugging**
Transitioning from a monolith on a single VM to an ephemeral, orchestrated cluster means you can no longer simply "SSH in and tail the application log file." Components are distributed dynamically across transient network pods. If a user order fails silently, tracking down which exact Pod or worker handled that specific fraction of the request is substantially harder.

**How do we mitigate it?** 
We will implement **Centralized Log Aggregation**. Containers are strictly required to stream logs to `stdout` and `stderr`. A node-level DaemonSet agent (like Promtail or AWS CloudWatch Agent) will automatically scrape those logs from the orchestrator and forward them into a centralized platform. Developers will query logs entirely via the aggregator UI using correlation-IDs, bypassing the need to directly access compute-layer shells. For local dev cycles, we will use `docker-compose` to emulate the container orchestration boundary natively on developer laptops.
