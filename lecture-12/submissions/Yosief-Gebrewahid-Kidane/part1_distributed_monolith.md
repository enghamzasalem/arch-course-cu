# Part 1 — Distributed Monolith Anti-Patterns (CityBite)

## 1. Overview

Simply splitting a monolithic application into multiple services does not automatically create a good microservice architecture. If services remain tightly coupled through shared databases, synchronized deployments, or excessive cross-service communication, the system becomes a **distributed monolith**.

In this situation, teams experience the operational complexity of microservices without gaining real flexibility or independence.

---

# 2. Red Flag #1 — Shared Database Across Services

## Problem

If multiple services directly access the same PostgreSQL tables, service boundaries become meaningless. A schema change made by one team can unexpectedly break another service.

For example:
- Payments service directly reading `orders` tables
- Dispatch service updating restaurant records
- Shared joins across contexts

This creates hidden coupling between teams and prevents independent deployments.

---

## Why This Is Dangerous

- Database migrations become risky
- Teams cannot evolve schemas independently
- One slow query can impact every service
- Tight coupling remains even if APIs are separated

---

## Mitigation

CityBite should gradually adopt a **database-per-service** model where each bounded context owns its own schema or datastore.

Cross-context communication should happen through:
- APIs
- Events
- Read models
- Async replication

instead of direct SQL joins.

---

# 3. Red Flag #2 — Synchronized Deployments

## Problem

If every service must be deployed together, the system behaves like a monolith operationally.

Example:
- Payments API changes force Ordering deployment
- Dispatch changes require Notification updates
- Entire platform released as one large deployment

---

## Why This Is Dangerous

- Slower release cycles
- Higher deployment risk
- Small changes require full regression testing
- Teams block each other frequently

---

## Mitigation

CityBite should support:
- Independent deployments
- Backward-compatible APIs
- Additive API evolution
- Feature flags and gradual rollouts

Using tolerant contracts allows one service to evolve without forcing immediate upgrades elsewhere.

---

# 4. Red Flag #3 — Excessive Synchronous Service Calls

## Problem

A distributed monolith often replaces local function calls with chains of synchronous HTTP requests.

Example:
- Ordering → Payments → Dispatch → Notifications
- One failed dependency breaks the entire request chain

---

## Why This Is Dangerous

- Higher latency
- Cascading failures
- Reduced availability
- Difficult debugging during incidents

During dinner rush traffic, even one slow dependency can create retry storms and overload the platform.

---

## Mitigation

CityBite should prefer asynchronous communication for non-critical workflows.

Recommended patterns:
- Queues
- Event-driven processing
- Worker pools
- Retry queues with backoff

Only truly critical operations, such as payment authorization during checkout, should remain synchronous.

