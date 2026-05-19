# Part 3.2: Autoscaling and Backpressure

## 1. Kubernetes HPA Configuration for the Order API
To survive the dynamic dinner rushes, the Order API pods must auto-scale based on real workload pressure.
- **Metric:** Average CPU Utilization. *(Assumption: The API is computationally bound by JSON parsing and validation rather than memory)*
- **Target:** 70% CPU.
- **Min Replicas:** 3 *(To ensure baseline high availability across multiple availability zones and handle localized node failures)*.
- **Max Replicas:** 30 *(Calculated securely based on the maximum expected concurrent connections our database tier can safely handle without exhausting the connection pool)*.

## 2. Backpressure Policy
When a downstream service (e.g., a third-party mapping API or our own dispatch worker queue) begins to fail or timeout, we implement a **Circuit Breaker with Graceful Degradation**. Instead of allowing HTTP requests to stack up and crash the Order API waiting for I/O, the system instantly halts non-critical external requests. If the driver dispatch queue depth exceeds 50,000 messages, checkout requests immediately degrade by returning an HTTP 503 Service Unavailable with a `Retry-After: 30` header. We actively shed load to protect the platform's core memory.

## 3. The Failure Paradox: Scaling Stateless Pods vs. Stateful Databases
If an engineer configures the Kubernetes HPA to allow the stateless API pods to scale infinitely (e.g., Max Replicas: 200) but forgets to adjust the PostgreSQL database tier, a massive failure cascade will occur. As traffic spikes, Kubernetes will greedily launch dozens of new API pods. Each of those 200 pods will attempt to open a database connection pool (e.g., 20 connections per pod). 

The Postgres instance, statically configured to only accept 500 max connections, will instantly saturate and start rejecting connections with `FATAL: sorry, too many clients already`. 

**Symptoms & Detection:** The API pods will report high health internally but every single transaction will result in 500 Internal Server Errors. Monitoring will show DB CPU dropping or flatlining while connection limits hit 100%. 

**Mitigation:** To mitigate this, we must enforce a connection multiplexer like `PgBouncer` in front of the database, cap the maximum API pod scale tightly to the database's known limits, and quickly shed load at the API layer before it reaches the data tier.
