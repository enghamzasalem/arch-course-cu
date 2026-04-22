**[Task 1.1 - Deployability assessment]{.underline}**

1.  **Deployability Risks and Mitigations:** The current \"Pets-on-VMs\"
    approach creates significant overhead and risk. Below are five
    identified bottlenecks and their Kubernetes-native solutions:

  -----------------------------------------------------------------------
  **Risk /         Impact                      Kubernetes/Container
  Bottleneck**                                 Mitigation
  ---------------- --------------------------- --------------------------
  Host Drift       Manual SSH scripts lead to  **Immutable Images:** Use
  (Snowflakes)     VMs having different        Docker to package the OS,
                   library versions or OS      Python runtime, and
                   patches over time.          dependencies into a single
                                               image digest. What runs on
                                               a laptop is identical to
                                               what runs in production.

  Coupled Disk     Storing menu JPEGs in       **PersistentVolumeClaims
  Layout           /var/citybite/uploads       (PVC):** Abstract storage
                   prevents scaling; a new VM  away from the node. Use a
                   won\'t have the old images. ReadWriteMany volume (like
                                               AWS EFS) or move to Object
                                               Storage (S3) so all Pods
                                               see the same data.

  Configuration    .env files manually edited  **ConfigMaps & Secrets:**
  Sprawl           on disk lead to \"it works  Inject configuration via
                   on my machine\" errors and  environment variables at
                   leaked secrets.             runtime. Use an **External
                                               Secrets Operator** to pull
                                               values securely from a
                                               cloud vault (e.g., AWS
                                               Secrets Manager).

  High-Stakes      Restarting the monolith     **RollingUpdate
  Deployments      causes downtime. Rollbacks  Strategy:** Kubernetes
                   require manual script       orchestrates a gradual
                   reversal.                   rollout, ensuring new Pods
                                               are \"Healthy\" before
                                               terminating old ones.
                                               Rollbacks are a single
                                               command: kubectl rollout
                                               undo.

  Opaque Health    SSH scripts don\'t know if  **Liveness & Readiness
  Checks           the *app* is actually       Probes:** The cluster
                   working, only if the        actively monitors the
                   *process* is running.       /health endpoint. If the
                                               app deadlocks, Kubernetes
                                               automatically restarts the
                                               container.
  -----------------------------------------------------------------------

2.  **The New Complexity: Observability:**

-   **What becomes harder:** In the VM model, you could SSH in and check
    a single log file. In Kubernetes, logs are ephemeral; if a Pod
    crashes and restarts, the logs are gone. Debugging distributed
    networking issues (Service-to-Pod) is also more complex than local
    loopback.

-   **Mitigation:** Implement Centralized Logging and Monitoring. Use a
    \"sidecar\" pattern or a log forwarder (like Fluentbit) to send all
    stdout/stderr logs to a persistent store (e.g., CloudWatch or ELK
    stack). Pair this with Structured Logging (JSON) to make searching
    across multiple Pods easier.
