# Part 3.2: Autoscaling and System Limits

## Horizontal Pod Autoscaling (HPA)

CityBite uses Horizontal Pod Autoscaling (HPA) for the Order API to handle traffic spikes. The HPA can scale based on CPU utilization or request rate.

Example configuration (assumptions):
- Metric: CPU utilization
- Target: 70%
- Minimum replicas: 3
- Maximum replicas: 20

This allows the system to automatically increase the number of API pods during peak traffic and reduce them during low usage, optimizing resource usage and cost.

## Backpressure and Degradation Strategy

When downstream systems such as the database or external services become overloaded, CityBite must apply backpressure strategies.

Example strategies:
- Limit queue size to avoid unbounded growth
- Return HTTP 503 with a Retry-After header when the system is overloaded
- Disable non-critical features (e.g. analytics or recommendations)
- Delay or drop low-priority tasks

These mechanisms help protect the system from cascading failures.

## Failure Scenario: Scaling API but Not Database

If CityBite scales only the stateless API pods but does not scale the database, several problems occur:

- Database CPU usage becomes very high
- Connection pool gets exhausted
- Increased latency for all requests
- Timeouts and failed transactions
- API pods become idle waiting for database responses

This situation creates a bottleneck at the database level. It can be detected through monitoring metrics such as high query latency and connection usage.

Mitigation strategies include:
- Adding read replicas for read-heavy workloads
- Optimizing queries and indexing
- Introducing caching layers
- Increasing database resources (vertical scaling)