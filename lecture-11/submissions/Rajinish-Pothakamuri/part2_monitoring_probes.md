### Part 2: Monitoring and Failure Containment

**Task 2.1: Monitoring and Probes**

**1. Liveness and Readiness Probes for the Order Application Programming Interface**
Liveness probes determine whether the core application process is currently executing and has not entered an unrecoverable state, such as an application deadlock. For the Order application programming interface, this probe targets a foundational endpoint, explicitly defined as the `/healthz` path, to prove strictly that the underlying container runtime and application process are active. If this probe fails across consecutive checks, the Kubernetes orchestrator enacts a hard failure action by terminating and restarting the failing pod. 

In contrast, readiness probes verify whether the application is fully initialized and possesses the necessary operational capacity to process incoming user traffic. The corresponding endpoint, explicitly defined as the `/readyz` path, must prove that the application can successfully communicate with essential infrastructure. If the readiness probe fails, the orchestrator executes a soft failure action by temporarily removing the pod from the service load balancer. This immediately prevents the routing of new network traffic to the degraded instance until its operational capacity is restored.

**2. The Risk of Shallow Health Checks Under Pool Exhaustion**
Drawing upon the principles demonstrated in `example2_availability_monitoring_citybite.py`, relying on a shallow health check that unconditionally returns a successful status code can misrepresent system health during resource saturation. Under conditions of high concurrency, the application may exhaust its database connection pool. In this scenario, the application process remains actively running but is fundamentally incapable of fulfilling new checkout operations. A shallow probe on `/healthz` will falsely report the pod as operational, causing the load balancer to continuously route user traffic to an unresponsive instance, effectively multiplying the failure. Therefore, a meaningful readiness probe must execute a deep check—explicitly attempting to acquire a database connection—to accurately reflect the actual user-visible availability of the system.

**3. Synthetic Black-Box Probes**
To monitor systemic availability from the exact perspective of an end-user, the architecture employs a synthetic black-box watchdog probe operating continuously from an external geographic location outside the internal cluster network. This external monitor programmatically simulates a critical user journey, such as adding an item to a cart and initializing a checkout session via the public ingress. The synthetic probe explicitly asserts two critical conditions: first, that the public application programming interface remains entirely reachable over the external internet, and second, that the complete end-to-end response payload is successfully generated within a strict latency threshold.

**4. Alerting Thresholds and Runbooks**
**Alert One: Elevated Checkout Latency**
Threshold: The ninety-fifth percentile response time for the checkout endpoint exceeds two seconds for a sustained window of three consecutive minutes.
Runbook First Step: Operators must immediately inspect the external payment gateway latency metrics to rule out a third-party service degradation, followed by a review of the database processing unit utilization.

**Alert Two: Widespread Readiness Failures**
Threshold: More than twenty percent of the active Order application programming interface pods fail their readiness probes concurrently.
Runbook First Step: Operators must examine the database connection pool metrics to determine if connection starvation has occurred and assess whether duplicate heavy queries are causing a severe internal bottleneck.