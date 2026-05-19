# Part 3.1: Pattern Checklist

### Load Balancing
CityBite heavily utilizes **Load Balancing** at the edge using Kubernetes Ingress controllers. When a user requests to view a menu or check out, the load balancer distributes that HTTPS traffic in a round-robin fashion across the active Order API Pods. This protects any single container from becoming overwhelmed with connections during the 7 PM dinner rush and allows for horizontal scaling.

### Sharding / Partitioning
Database **Sharding** is **not** our first choice right now because of its extreme operational complexity and the need to overhaul application logic to perform cross-shard joins. Instead, we use logical **Partitioning Keys** (like indexing by `restaurant_id`) within a single vertical PostgreSQL instance. If we grow globally, we might eventually partition databases by geographic city limits (e.g., New York City vs. London), but for regional scale, a single indexed primary handles the load safely.

### Scatter / Gather
We might utilize the **Scatter/Gather** pattern for our dispatch algorithm. When an order is ready, the system needs to find the optimal delivery driver. It "scatters" a query to a geospacial microservice and a driver availability cache concurrently, and then "gathers" the results back to calculate the fastest ETA. This parallelizes heavy read requests and speeds up driver allocation significantly.

### Master / Worker (Worker Pool)
The **Master/Worker** pattern is the foundation of our asynchronous architecture. The Order API (Master) securely commits the financial transaction and then drops an event on the RabbitMQ queue. An auto-scaled pool of background pods (Workers) consume these events to execute slow external I/O tasks like sending emails and notifying kitchen tablets. 

### Multi-Tenant Fairness
To ensure **Multi-Tenant Fairness**, we implement strict rate-limiting per `restaurant_id` and token bucket algorithms on the API Gateway. If a massive chain goes viral on TikTok and receives 10,000 orders a minute, we aggressively throttle their specific partition or route their background events to a dedicated slow-lane queue. This prevents a single viral restaurant from starving CPU and Database connections for the other thousands of quiet neighborhood restaurants on our platform.
