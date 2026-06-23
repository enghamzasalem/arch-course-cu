# Part 1 — Deployability Assessment: CityBite on Kubernetes

## 1. Current situation: pets-on-VMs

CityBite is currently deployed on long-lived virtual machines hosted in the cloud. These VMs behave like "pets": they are individually managed, manually configured, and treated as unique servers that must be maintained carefully over time.

A typical deployment in this model involves updating application code directly on one or more VMs, restarting services manually, and verifying that the system still works. Configuration may be partially stored on the servers themselves, which increases the risk of drift between environments.

This architecture creates operational friction because deployment depends on the condition of specific machines rather than on a repeatable platform abstraction.

## 2. Deployability assessment of the current architecture

The current deployability of CityBite is weak to moderate.

### 2.1 Release speed

Release speed is limited because deployments require manual work on existing VMs. A release may involve copying files, pulling code, installing dependencies, restarting services, and checking logs manually. This increases the time required to push changes to production.

### 2.2 Release safety

Release safety is also limited. If a new version causes errors, rollback may require restoring an older build manually or reconfiguring the VM to a previous state. This is slower and riskier than switching traffic back to a known-good deployment artifact.

### 2.3 Environment consistency

Environment consistency is poor compared with a containerized platform. Development, CI, and production may differ in OS packages, runtime versions, environment variables, or installed tools. This leads to "works on my machine" problems and unreliable deployments.

### 2.4 Scalability of deployment operations

Scaling in a pets-on-VMs setup is cumbersome. To increase capacity, the team may need to provision more VMs manually, duplicate configuration, and ensure that all nodes are running the same version. This creates operational overhead and slows down releases.

### 2.5 Failure recovery

Recovery is slower because specific VMs matter. If a VM fails, the service may depend on manually repairing or replacing that machine. The deployment model is therefore less resilient than an orchestrated container platform where failed instances are recreated automatically.

## 3. Main deployability problems

The main deployability issues in the current architecture are:

- manual deployment steps
- inconsistent runtime environments
- machine-specific configuration
- difficult rollback procedures
- slow recovery from failures
- limited release automation
- weak support for rapid, frequent deployments

Together, these issues reduce release cadence and increase deployment risk.

## 4. Target architecture on Kubernetes (AWS)

The proposed target architecture moves CityBite from pets-on-VMs to Kubernetes on AWS.

The new platform uses:

- **Amazon EKS** for container orchestration
- **Amazon ECR** for storing container images
- **AWS ALB** with Kubernetes Ingress for incoming traffic
- **Kubernetes Deployments and Services** for application components
- **Kubernetes ConfigMaps and Secrets** for configuration management
- **Amazon RDS** for the relational database (managed service outside the cluster)
- **Horizontal Pod Autoscaling** for demand-based scaling

> **Note on state management:** The relational database (PostgreSQL) runs on Amazon RDS outside the Kubernetes cluster. This is a deliberate design choice because stateful workloads are more complex to operate on Kubernetes. RDS provides managed backups, failover, and maintenance. Only stateless or lightly stateful components (cache, queue) run inside the cluster.

In this model, application services are packaged as immutable container images and deployed as replicated pods. Kubernetes manages scheduling, restarts unhealthy containers, and supports rolling updates.

## 5. How the new architecture improves deployability

### 5.1 Faster releases

Container images provide a consistent deployment artifact. Instead of changing machines manually, the team builds an image once and deploys it through Kubernetes. This reduces release time and supports a higher deployment frequency.

### 5.2 Safer rollouts

Kubernetes supports rolling updates, which means the new version can be introduced gradually while keeping the service available. If health checks fail, rollout can be paused or reversed. This makes releases safer than direct VM replacement.

### 5.3 Easier rollback

Rollback becomes easier because previous container versions remain available in the registry and Kubernetes can redeploy an older version quickly. This reduces the operational effort during incidents.

### 5.4 Better environment consistency

Containers package the runtime dependencies with the application. This improves consistency across development, CI, and production. The gap between "tested artifact" and "production artifact" becomes much smaller.

### 5.5 Better resilience

Kubernetes continuously monitors pod health and replaces failed instances automatically. Because workloads run as managed replicas rather than as unique machines, the platform is more fault tolerant.

### 5.6 Better scaling and operational repeatability

Scaling becomes a platform concern instead of a manual server-management task. Replicas can be increased declaratively, and the same deployment process can be reused across environments. This improves operational repeatability and reduces human error.

## 6. Measurable metrics comparison

| Aspect | Before (pets-on-VMs) | After (Kubernetes on AWS) |
|--------|----------------------|----------------------------|
| Deployment time | 10–30 minutes | 30–60 seconds (pod startup) |
| Rollback time | 10–20 minutes (manual) | < 30 seconds (`kubectl rollout undo`) |
| Time to scale (+ replicas) | Hours (provision VM, configure) | Seconds (adjust replicas) |
| Recovery from crash | 15+ minutes (manual repair) | < 1 minute (auto-restart) |
| Environment drift | High (config on VMs) | Low (immutable images + etcd) |
| Deployment frequency | Weekly or slower | Multiple times per day |
| Failure detection | Manual monitoring | Automatic (liveness probes) |

## 7. Before vs after summary

### Before: pets-on-VMs
- manually managed VMs
- server-specific configuration
- slow and risky deployments
- difficult rollback
- environment drift
- scaling and recovery require manual intervention

### After: Kubernetes on AWS
- container-based deployments
- consistent runtime environments
- rolling updates and faster rollback
- automated restarts and self-healing
- declarative scaling
- stronger support for frequent and reliable releases

## 8. Conclusion

The migration of CityBite from pets-on-VMs to Kubernetes on AWS significantly improves deployability. The new architecture increases release cadence, reduces deployment risk, improves consistency across environments, and provides a stronger operational foundation for continuous delivery. The trade-offs include increased operational complexity and the need to manage stateful workloads carefully (e.g., using RDS for the database outside the cluster).