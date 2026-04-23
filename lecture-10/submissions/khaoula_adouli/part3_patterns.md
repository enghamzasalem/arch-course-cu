# Part 3.1 - Scalability Pattern Checklist (CityBite)

## Load balancing

CityBite should load balance all API traffic across multiple Order API pods behind Kubernetes Service/Ingress. This is the first line of horizontal scaling for stateless compute and helps absorb dinner spikes. It should use health checks and zone-aware routing to avoid sending traffic to degraded pods. For fairness, rate limiting should be tenant-aware so one viral restaurant or partner batch client does not consume all available request budget.

## Sharding / partitioning

For Year 1, CityBite should prioritize partition-friendly schema and indexes before full physical sharding. The main hot path is restaurant active orders, so data access should use `restaurant_id`-centric keys to keep query scope local. True sharding is not first choice yet because operational complexity (rebalancing, cross-shard joins, tooling) is high. However, growth planning should define a future partition strategy so one high-traffic tenant does not dominate a single data segment.

## Scatter / gather

Scatter/gather can help in read-heavy dashboards where data comes from multiple services (orders, courier status, campaign metrics). For checkout-critical paths, it should be minimized because fan-out increases tail latency and failure surface. If used, CityBite should set strict timeouts and partial-response behavior rather than block the full user flow. Tenant fairness requires bounded fan-out per tenant and circuit breakers so one noisy tenant does not degrade everyone.

## Master / worker (worker pool)

CityBite should use a worker-pool pattern for asynchronous side effects after order creation (notifications, webhook delivery, some analytics). API layer acts as ingress/master of accepted work, queue stores backlog, workers process in parallel and can be autoscaled by queue depth. This decouples customer checkout latency from third-party notification latency. Fairness can be enforced by per-tenant queue partitioning or weighted worker scheduling so one viral restaurant does not starve other restaurants.
