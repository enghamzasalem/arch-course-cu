# Part 1 — Task 1.2: Anti-Pattern Check — Distributed Monolith

---

## Definition (Lecture 12)

A **distributed monolith** is a system that has been split into multiple deployed processes yet retains the coupling characteristics of a monolith: services cannot be deployed, scaled, or failed independently, and a change in one service still forces coordinated changes in others. It combines the operational complexity of a distributed system with none of the autonomy benefits of true microservices. The lecture frames this as the worst of both worlds — you pay the latency and ops tax of distribution while keeping the tight coupling that motivated the split in the first place.

---

## Red Flag 1 — Shared Database / Shared Schema

### Description

All "services" write to and read from the same Postgres instance using the same schema — or a nominally separate schema where services freely join across each other's tables. In CityBite's baseline, the shared Postgres schema is explicitly named as a pain point: "one schema slows teams." If the payment extraction debate ends with a `PaymentService` process that still `SELECT`s from the `orders` table to resolve a payment, or the Dispatch service joins `menu_items` for restaurant metadata, the database is the real integration point. The service boundary is a deployment fiction.

**Why this is the distributed monolith signal:** The lecture defines database-per-service as a required condition for context independence. When services share a schema, any schema migration — adding a column, renaming a table, changing a constraint — must be coordinated across every team simultaneously. Independent deployability is gone. The shared Postgres schema is structurally equivalent to shared memory in a monolith; it just has network latency added.

### Mitigation — Database-per-Context with an Anti-Corruption Layer

Each bounded context from Task 1.1 owns a **logically separate schema** (enforced via Postgres `SCHEMA`-level grants at minimum; separate Postgres instances per context at extraction time). Cross-context data needs are satisfied by **events or API calls, never direct joins**. For example, when Dispatch needs the restaurant address, it calls the Catalogue API and caches the result locally in its own schema — it does not join `catalogue.restaurants`. Where legacy shared tables exist during migration, an **anti-corruption layer** (a thin read-only adapter in the extracting service) translates the shared-schema shape into the context's own model without letting the foreign schema bleed into domain logic.

---

## Red Flag 2 — Synchronous Chains of Calls (Temporal Coupling)

### Description

A customer places an order and the Ordering service makes a synchronous HTTP call to Payment, which synchronously calls Fraud Detection, which synchronously calls an external scoring API, which calls a notification pre-flight check — all in the critical path of a single request. Every hop must succeed for the customer to receive a response. If the Fraud Detection service deploys a bad build and goes down, the entire checkout flow fails, even though Payment and Ordering are "separate services."

**Why this is the distributed monolith signal:** Lecture 12 distinguishes between structural coupling (shared code, shared schema) and **temporal coupling** — the requirement that all participants be available at the same time for the flow to succeed. A chain of synchronous calls across service boundaries means uptime is now the product of each service's availability: if each of five services is 99.9% available, the chain's availability is 99.9%^5 ≈ 99.5%. The services are not independently operable; they fail together. This is monolith-style availability in a distributed wrapper.

### Mitigation — Async Events for Non-Blocking Steps + Circuit Breakers for Unavoidable Sync Calls

Steps that do not require an immediate answer — fraud scoring, notification pre-flight, dispatch assignment — are moved to **async event consumers** off the critical path (using the Postgres outbox pattern already in the Lecture 9 baseline). The checkout critical path is reduced to: Ordering → Payment authorisation (sync, required) → return confirmation to customer. Everything else is event-driven. For the remaining synchronous call to Payment, a **circuit breaker** (Lecture 11 availability pattern) prevents a slow payment gateway from holding Ordering threads open: after a threshold of failures the circuit opens, returns a fast failure, and retries with exponential backoff. Temporal coupling is not eliminated but is isolated to the one hop that genuinely requires it.

---

## Red Flag 3 — Lockstep Deployment (Release Coupling)

### Description

Every time the Ordering service changes the shape of the `OrderStatusChanged` event — adding a field, renaming a key — the team must deploy Dispatch, Notifications, and Payment simultaneously because all of them parse that event with no tolerance for unknown fields or missing keys. Sprint planning devolves into cross-team deployment windows. "Microservice" releases are coordinated like a monolith release train. The `order_v2_breaking_rename` example in `example2_flexibility_api_evolution_citybite.py` illustrates exactly this: renaming `orderId` to `id` silently breaks every consumer that reads `payload.get("orderId")` without a coordinated deploy.

**Why this is the distributed monolith signal:** Independent deployability is the defining operational benefit of microservices (Lecture 12). If teams cannot deploy their service on their own schedule — because their consumers depend on the exact current shape of their API or event schema — they are operationally a monolith. The number of deployment processes is irrelevant; the coupling is in the contracts.

### Mitigation — Additive-Only Schema Evolution + Consumer-Driven Contract Tests

Publishers follow the **additive-only rule** from `example2`: new optional fields are added without removing or renaming existing fields, so old consumers continue to function (tolerant-reader pattern). When a breaking change is unavoidable, the publisher ships a `/v2` endpoint or a versioned event topic alongside `/v1` and runs both during a deprecation window with an explicit sunset date communicated to consumer teams. This is enforced not just by policy but by **consumer-driven contract tests** (e.g. Pact): each consumer registers the exact fields it reads, and the publisher's CI pipeline fails if a proposed change would break any registered consumer. Deployment coupling is replaced by automated contract verification — teams deploy independently and the test suite catches incompatibilities before production.

---

---

*Vocabulary aligned with Lecture 12 (Chapter 12: Flexibility and Microservices), example1_flexibility_coupling_citybite.py (PaymentPort / ports-and-adapters), and example2_flexibility_api_evolution_citybite.py (additive vs breaking JSON change).*
