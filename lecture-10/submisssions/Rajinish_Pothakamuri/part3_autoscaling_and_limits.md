## Part 3.2: Autoscaling and Backpressure

This section outlines the operational strategies CityBite uses to maintain stability during traffic spikes and downstream failures.

### 1. Horizontal Pod Autoscaler (HPA) Rule: Order API

To handle peak periods such as the dinner rush, the Order API is configured with a Horizontal Pod Autoscaler that adjusts capacity based on demand.

* **Metric:** Average CPU Utilization with a target of 70 percent
* **Reasoning:** CPU-based scaling is appropriate because the Order API performs compute-heavy tasks such as request validation and JSON processing. A 70 percent target provides headroom so that new pods can be created before existing ones become overloaded, helping maintain stable response times.
* **Min Replicas:** 3, to ensure availability across nodes
* **Max Replicas:** 20, to control infrastructure cost and avoid exhausting PostgreSQL connection limits

---

### 2. Backpressure and Degradation Policies

When downstream systems such as the database or payment services slow down or fail, CityBite applies backpressure and controlled degradation to protect the system.

* **Queue Depth Limit:** The notification queue has a defined maximum size. If workers cannot keep up and the queue fills, the API stops accepting non-critical background tasks. This prevents memory exhaustion and protects core functionality.

* **Graceful Degradation:** During extreme load, non-essential features such as live driver tracking or personalized recommendations are temporarily disabled. This reduces database and compute load so that critical operations like order placement continue to function reliably.

* **503 with Retry-After:** If the system reaches full capacity, the load balancer returns a 503 Service Unavailable response with a Retry-After header. This signals clients to pause before retrying, preventing repeated rapid requests that could worsen system overload.

---

### 3. Failure Lesson: Scaling Stateless Pods vs Stateful Database

If the stateless Order API is scaled aggressively without scaling the PostgreSQL database, the system can experience a cascading failure.

* **Symptoms:** Although more API pods are running, performance quickly degrades. Latency increases significantly, the database reaches full CPU utilization, and errors such as connection exhaustion occur because each pod attempts to open database connections.

* **Detection:** This issue can be identified by observing a mismatch between increasing API replicas and declining successful transaction rates. Monitoring tools may also show high database CPU usage and lock contention.

* **Mitigation:** In the short term, the API should be throttled by reducing the maximum number of replicas to a level the database can support. In the long term, architectural improvements such as adding read replicas for query offloading or implementing database partitioning are required to scale effectively.