# Part 1: Contexts & Conway
## Task 1.2: Anti-pattern Check — Distributed Monolith

## 1. Overview
A distributed monolith is a system that is split into multiple services on paper, but still behaves like one tightly coupled application in practice. CityBite should avoid this because it would keep the operational cost of microservices without getting their flexibility benefits.

---

## 2. Red Flag 1: Shared Database Schema

If every “microservice” reads and writes the same PostgreSQL schema, the system is still a distributed monolith. In that case, teams may deploy separate services, but they remain blocked by the same tables, migrations, and lock contention. A schema change in one area can break other services, which means the boundaries are not real.

### Mitigation
Move toward **database per service** or at least separate schemas with strict ownership. Each service should own its own data model and publish events or APIs for other contexts instead of letting them query the same tables directly.

---

## 3. Red Flag 2: Synchronous Call Chains Across Many Services

If a single user action makes a long chain of synchronous calls such as Order → Payments → Restaurant → Dispatch → Notifications, the system behaves like one large app spread across the network. Latency adds up, and one slow or failing dependency can take down the whole request path. This turns service boundaries into a fragile distributed transaction.

### Mitigation
Use **asynchronous events** for non-critical follow-up work and keep the critical path short. For example, checkout should complete after the core order and payment steps, while notifications and dispatch updates can happen later through events or queues.

---

## 4. Red Flag 3: Coordinated Releases and Shared Ownership

If every service must be released together because of shared contracts, hidden dependencies, or one team owning all services, then the “microservices” are only separated at deployment time. This creates the same coordination pain as a monolith, but with more moving parts. Teams will avoid independent changes because they fear breaking downstream services.

### Mitigation
Strengthen **bounded contexts, contract tests, and independent deployment rules**. Each service should have a stable public API or event contract, and changes should be made in an additive way whenever possible. Separate teams or clearly assigned ownership can also reduce accidental coupling.

---

## 5. Summary
CityBite is drifting toward a distributed monolith if services share one database, depend on long synchronous chains, or cannot be released independently. The fix is not just “more services”; it is real boundary enforcement through data ownership, asynchronous integration, and contract discipline. A good microservice architecture should reduce coordination, not multiply it.
