# Part 1.2 — Distributed Monolith Anti-Patterns

## Red Flag 1 — Shared Database Between Services

If all CityBite services directly access the same PostgreSQL schema, the system becomes tightly coupled even if services are deployed separately.

### Why This Is a Problem
- Schema changes affect multiple services
- Teams cannot evolve independently
- Hidden dependencies increase operational risk

### Mitigation
Adopt a **database per service** approach where each bounded context owns its own data and exposes it only through APIs or events.

---

## Red Flag 2 — Synchronous Chains Between Services

If Order Service depends synchronously on Payment, Delivery, and Notification services for every request, failures can cascade across the system.

### Why This Is a Problem
- Increased latency
- Retry storms
- Reduced availability
- Tight runtime coupling

### Mitigation
Use asynchronous communication (events/queues) for non-critical operations such as notifications and delivery updates.

---

## Red Flag 3 — Coordinated Deployments

If all services must be deployed together because of tightly coupled APIs or breaking changes, the system behaves like a distributed monolith.

### Why This Is a Problem
- Independent deployment becomes impossible
- Increased downtime risk
- Slower feature delivery

### Mitigation
Use backward-compatible APIs, contract testing, and versioning strategies to allow services to evolve independently.

---

## Conclusion

Microservices alone do not guarantee flexibility.  
Without proper boundaries, independent data ownership, and loose coupling, CityBite could become a distributed monolith with higher operational complexity and little architectural benefit.