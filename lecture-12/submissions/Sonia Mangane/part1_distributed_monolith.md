# Task 1.2: Anti-pattern check — distributed monolith

A **distributed monolith** is a system that has been split into separate deployable services but still behaves like a monolith: services are tightly coupled, cannot be deployed independently, and a failure in one cascades to all others. It combines the operational complexity of microservices with none of the flexibility benefits.

---

## Red Flag 1: Synchronous Chain of Calls Across All Services

**What it looks like:** A single customer checkout triggers a synchronous HTTP call from Ordering to Payment to Dispatch to Notification to Restaurant, where each service waits for the next to respond before returning. If Notification is slow, the checkout times out. If Dispatch is down, payment cannot complete.

**Why it is a distributed monolith:** The services are deployed separately but are **runtime-coupled**. The system's availability is the product of all individual availabilities and a single slow service degrades the entire checkout flow. This is the same as a monolith, with added network latency.

**Mitigation:** Replace synchronous chains with **async events** wherever the caller does not need an immediate response. Ordering calls Payment synchronously but after that it publishes an `OrderConfirmed` event. Dispatch, Restaurant, and Notification subscribe independently. No service waits for another downstream service.

---

## Red Flag 2: Shared Database Across Services

**What it looks like:** The Ordering service and the Dispatch service both connect to the same Postgres instance and the same schema. Dispatch queries `orders.status` directly with a SQL join. Ordering updates `dispatch.courier_id` directly.

**Why it is a distributed monolith:** The database is the hidden coupling point. A schema migration in the Orders table breaks the Dispatch service even though they are "separate services". Teams cannot deploy independently because a DB change requires coordinating all consumers simultaneously. This is the exact pain described in the assignment baseline: "one schema slows teams".

**Mitigation:** Apply **database per service**  Each context owns its own logical scheme. Cross-context data needs are satisfied through API calls or event-driven read models, never direct SQL joins across service boundaries.

---

## Red Flag 3: Deployment Lockstep — Services Must Be Released Together

**What it looks like:** The Payment service's API response shape changes (e.g. a field is renamed from `transactionId` to `transaction_id`). Before deploying the new Payment service, the team must simultaneously deploy a new version of Ordering (which calls Payment) and a new version of the finance dashboard, which reads Payment responses. All three must go out at the same time or the system breaks.

**Why it is a distributed monolith:** Independent deployability is one of the core promises of microservices. If services must be released in lockstep, the team has not gained deployment flexibility — they have just made deployments harder by requiring coordination across multiple repositories and pipelines. This is the silent API change breaks mobile clients pain from the assignment baseline.

**Mitigation:** Enforce **API evolution rules**: only additive changes are allowed without a versioning strategy. Breaking changes require a `/v2` endpoint with a deprecation window, giving consumers time to migrate. Pair this with **consumer-driven contract tests** so the Payment team gets automated feedback if a proposed change would break a known consumer — before the change is deployed.
