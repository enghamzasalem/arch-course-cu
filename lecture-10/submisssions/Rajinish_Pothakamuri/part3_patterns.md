## Part 3.1: Pattern Checklist

This section maps key architectural patterns to the CityBite platform to support scalability and maintain multi-tenant fairness.

### Load Balancing

CityBite uses load balancing to distribute incoming traffic across multiple instances of the Order API. A strategy such as round-robin or least connections ensures that requests are evenly spread across available pods. The system exposes a single entry point through an Ingress, which hides the underlying replication from clients. This setup allows new API instances to be added or removed dynamically based on traffic, improving availability and handling peak demand without affecting the user experience.

---

### Sharding and Partitioning

To scale beyond the limits of a single PostgreSQL instance, CityBite can partition data across multiple database nodes. A suitable partition key is `restaurant_id`, as it aligns with the core business domain and keeps queries localized. This approach ensures that high traffic for one restaurant does not impact others, as each partition handles its own subset of data. While not required in early stages, this strategy becomes important when vertical scaling of the database reaches its limits.

---

### Scatter and Gather

CityBite applies the scatter and gather pattern when a request needs to query multiple data sources. For example, a global search for a food item such as pizza may require querying multiple partitions or services. The system sends requests to all relevant sources and combines the results into a single response. To maintain responsiveness, a timeout can be applied so that the system returns partial results if some sources are slow.

---

### Master and Worker (Worker Pool)

CityBite uses a worker pool pattern to process background tasks efficiently. The Order API acts as the coordinator by placing tasks onto a queue, while multiple worker instances process these tasks in parallel. This pattern is used for operations such as sending notifications or processing batch jobs. It improves scalability by separating time-consuming or external operations from the main request flow, allowing the API to remain responsive.

---

### Multi-tenant Fairness

CityBite ensures fair resource usage across all restaurants by applying controls at both the application and database levels. Using `restaurant_id` as a partition key allows the system to isolate workloads per tenant. Rate limiting and resource quotas can be applied to prevent a single high-traffic restaurant from consuming excessive CPU, database connections, or query capacity. This ensures consistent performance and reliability for all users on the platform.

