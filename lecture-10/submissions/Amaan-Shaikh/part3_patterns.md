# Part 3.1 – Scalability Patterns Checklist

## Load Balancing

CityBite already uses Kubernetes Service + Ingress to distribute traffic across API pods. This is essential for horizontal scaling. The same pattern applies to workers pulling from SQS.

**Choice:** Required.

## Sharding / Partitioning

CityBite can shard orders by `restaurant_id` or `city_id`. Each shard lives in its own database. Queries for a restaurant only hit one shard. This solves the single-writer bottleneck but adds complexity.

**Choice:** Not for Year 1. Use read replicas first. Sharding if orders exceed 10M/month.

## Scatter / Gather

A dashboard that queries all restaurants would need scatter/gather: send query to each shard, then combine results. CityBite avoids this pattern because each restaurant only sees its own data.

**Choice:** Avoided. Restaurant isolation prevents scatter/gather.

## Master / Worker (Worker Pool)

Exactly what the notification queue implements: API (master) pushes jobs to SQS; worker pods pull and process. Works well for async out-of-band tasks (email, push, analytics).

**Choice:** Implemented for notifications.

## Multi-Tenant Fairness

A viral restaurant with 10x normal orders must not starve other restaurants. Mitigations:

- Pools per restaurant (soft limit on workers)
- Query index on `restaurant_id` prevents one restaurant's rows from scanning all others
- Connection pool per restaurant (advanced)
- SQS queue per large restaurant (future)

**Basic approach for Year 1:** Monitor; if one restaurant misbehaves, rate-limit at API.

## Summary Table

| Pattern | CityBite Use | Priority |
|---------|--------------|----------|
| Load balancing | API pods + Ingress | Required |
| Read replicas | Dashboard + menu reads | High |
| Queue + workers | Notifications | High |
| Cache (Redis) | Menu items | Medium |
| Sharding | Orders database | Future |
| Scatter/gather | Avoided | Not used |