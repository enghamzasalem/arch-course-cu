# Task 3.1: Pattern checklist


### Load Balancing
CityBite uses an Application Load Balancer to spread incoming traffic across multiple API pods. If one pod crashes, the load balancer sends traffic to the healthy ones.
This lets us add or remove pods without the mobile app needing to know anything about server IPs.

### Sharding / Partitioning
We don’t plan to shard in Year 1, but the system is built so we can shard later.
When the database gets too big, we can split it by region (e.g., Munich DB vs. Bremen DB).
That way, a busy night in one city doesn’t slow down another.

### Scatter / Gather
For global searches (like “best tacos near me”), the API sends the same query to multiple regions at once. Each region returns its results, and the API merges them into one final list. This keeps searches fast even as the number of restaurants grows.

### Master / Worker (Worker Pool)
The API handles quick tasks and pushes slow tasks into a queue.
Workers pick up those tasks in the background, things like sending receipts or dispatching drivers. This keeps the app fast even if third‑party services are slow.

### Multi-tenant Fairness
To prevent one super‑popular restaurant from hogging all the resources, we use rate limits and quotas. This stops “noisy neighbors” from overwhelming the system and ensures every restaurant still gets their orders.