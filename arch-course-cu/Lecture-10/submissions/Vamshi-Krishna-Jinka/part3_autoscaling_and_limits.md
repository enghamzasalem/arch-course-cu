# Part 3: Autoscaling and Backpressure
## Task 3.2: Autoscaling and Backpressure

## 1. Proposed HPA Rule for the Order API

### Assumption
These numbers are assumed for a medium-sized CityBite deployment during dinner rush.

### HPA rule
- **Metric:** CPU utilization
- **Target:** 65% average CPU per pod
- **Minimum replicas:** 3
- **Maximum replicas:** 20

### Why this metric
The Order API is stateless, so it is a good candidate for horizontal scaling. CPU is a practical first signal because traffic spikes usually increase request parsing, validation, serialization, and database request handling. If CPU stays below the target, the system can keep fewer pods; when traffic rises, Kubernetes can add more pods before latency gets too high.

---

## 2. Backpressure / Degradation Policy

When downstream systems slow down, the API should protect the checkout path instead of letting the whole cluster fail.

### Policy
- Limit the queue depth for background jobs such as notifications and analytics.
- If the queue is above the threshold, reject non-critical work.
- Return **503 Service Unavailable** with a **Retry-After** header for overloaded async requests.
- Temporarily disable non-critical features such as marketing banners, recommendation widgets, or slow analytics writes.

### Why this helps
This prevents the API from accepting more work than the workers or database can handle. It also gives clients a clear signal that the system is overloaded and that they should retry later.

---

## 3. Failure Lesson: Scaling Stateless Pods Without Scaling the Database

If CityBite scales only the Order API pods and forgets the database, the system will still slow down under load. The API pods may accept more traffic, but they will all compete for the same PostgreSQL connections and write capacity. Symptoms include rising p95 latency, connection pool exhaustion, timeouts, and repeated retry storms from clients. CPU on the API layer may look normal while the database CPU stays high and lock waits increase. The system may also show more failed checkouts even though Kubernetes reports that the pods are healthy. This is a common trap because the bottleneck moves from the stateless tier to the stateful tier. Detection usually comes from database metrics such as CPU, IOPS, active connections, lock contention, and slow query logs. The mitigation is to reduce database pressure with caching, read replicas, query optimization, partitioning, queues, and finally database scaling or schema redesign.

---

## 4. Summary
Autoscaling works best when it is tied to a real signal and paired with backpressure. For CityBite, the API layer can scale out quickly, but the database and downstream services must also be protected. A good scalability design adds more pods only when the rest of the system can absorb the traffic.
