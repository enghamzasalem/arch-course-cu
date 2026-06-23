# Part 3.1: Scalability Patterns for CityBite

## Load Balancing

CityBite uses load balancing at the ingress level to distribute incoming HTTPS requests across multiple Order API pods. This ensures that no single instance is overloaded during peak traffic periods such as dinner rush or marketing campaigns. Load balancing improves system responsiveness and availability by spreading the workload evenly. Without it, a single API instance could become a bottleneck and increase latency for users.

## Sharding / Partitioning

CityBite can use partitioning based on restaurant_id to improve database scalability. For example, queries for active orders in a restaurant should only scan data related to that restaurant instead of the entire dataset. This reduces query time and improves performance under high load. However, sharding is complex to manage and is not the first step in Year 1. It becomes useful when the database grows significantly.

## Scatter/Gather

Scatter/gather is useful when CityBite needs to aggregate data from multiple sources, such as combining restaurant menus, availability, and delivery estimates. The system sends parallel requests to multiple services and gathers the responses. This improves response time compared to sequential requests. However, it increases system complexity and is not always necessary for simple operations.

## Master/Worker (Worker Pool)

CityBite uses a master/worker pattern for handling asynchronous tasks such as sending notifications (email/SMS). The API acts as the master by enqueueing jobs into a queue, and worker processes consume and process these jobs independently. This decouples user requests from slow external operations and improves system scalability. It also allows horizontal scaling by adding more workers during peak load.

## Multi-Tenant Fairness

CityBite must ensure fairness across restaurants. A highly popular restaurant should not consume all system resources and degrade performance for others. This can be achieved through rate limiting, partitioning data by restaurant, and isolating workloads. For example, each restaurant's orders can be processed independently to prevent one tenant from starving others.