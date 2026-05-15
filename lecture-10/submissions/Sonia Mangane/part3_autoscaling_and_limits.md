# Task 3.2: Autoscaling and backpressure

## 1. HPA Rule (Order API)
We use Kubernetes HPA so the Order API can scale automatically during busy times.

* **When to scale:** CPU goes above 60%, or requests per second go above 400 per pod.
* **Pod limits:** * **Min:** 3 pods (for reliability)
    * **Max:** 40 pods (to avoid huge costs and DB overload)
* **Assumptions:** Each pod can handle about 500 active requests before slowing down.

## 2. Backpressure and Degradation Policy
If the database or payment system slows down, the API must protect itself instead of crashing.

* **Queue Depth Limits:** f the notification queue has 10,000+ messages, we stop sending non‑important jobs (like “Rate your meal”) and focus only on order‑critical tasks.
* **503 with Retry-After:** If the DB connection pool is full, the load balancer returns:
`503 Service Unavailable` + `Retry-After: 30`.
The app then waits 30 seconds instead of retrying instantly, avoiding a Retry Storm.
* **Feature Toggling:** During extreme load, we can turn off heavy features (like the ML delivery‑time model) and use a simple fallback estimate.

## 3. Failure Lesson: Scaling Stateless Pods vs. Stateful Database
A common mistake is scaling API pods without scaling the database.

**The Scenario:**
If traffic jumps 20× and HPA creates 40 pods, each pod opens its own DB connections.
This can overload Postgres even if the API pods are fine.

**Symptoms & Detection:**
* **Symptoms:** 
- Database hits max connections
- New orders fail with “cannot connect to database”
- Latency spikes even though CPU on pods is low
**Fix:**
To handle this safely, we need to:

- Scale the database vertically (more CPU/RAM), or
- Use a connection pooler like PgBouncer
Adding more API pods alone just makes the DB choke faster.