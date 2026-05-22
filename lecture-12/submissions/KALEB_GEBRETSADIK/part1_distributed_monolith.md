# Part 1.2: Anti-Pattern Check — Distributed Monolith

## Red Flags and Mitigations

### Red Flag 1: Synchronous Chain of Service Calls
If placing an order requires Order → Payment → Dispatch → Notifications to all respond synchronously before the user gets a receipt, the system is a distributed monolith. A failure in any hop fails the whole chain and latency compounds. This is tight runtime coupling disguised as "microservices."

**Mitigation:** Decouple non-blocking steps using **async events**. The Order context emits `OrderPaid`, and Dispatch/Notifications react independently. Only the critical Payment call stays synchronous.

---

### Red Flag 2: Shared Database
If two or more "separate services" (e.g. Ordering and Dispatch) query or write to the **same Postgres schema or tables**, there are no real service boundaries. Schema changes in one service break the other silently, and deployment must be coordinated — the classic monolith constraint.

**Mitigation:** Enforce **database per service** — each context owns its schema. Cross-context data needs are replaced with API calls or event-driven read models. No service may issue SQL that touches another service's tables.

---

### Red Flag 3: Deployment Lockstep
If all services must be deployed together (e.g., a version bump in the Payment service requires simultaneously deploying Order and Dispatch), the team has distributed the code but not the release cycle. The services share implicit contracts without versioning — a breaking change anywhere forces a coordinated rollout.

**Mitigation:** Introduce **consumer-driven contract tests** (e.g. with Pact) so each service publishes and verifies its API contract independently. Pair this with **additive API evolution** rules (per `example2`) so services can be deployed independently without coordination.
