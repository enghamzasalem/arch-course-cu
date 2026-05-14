# Part 1.2: Anti-Pattern Check — Distributed Monolith (CityBite)

A **distributed monolith** is a set of “services” that are **deployed separately** but still behave like one tightly coupled application: every change requires coordinated releases, failures cascade, and teams cannot evolve boundaries independently.

## Three red flags (lecture-aligned)

### 1. **Chatty synchronous chains across “services”**

**Red flag:** Placing an order triggers five+ **blocking** HTTP calls between internal services (catalog → pricing → inventory → payments → notifications) on the **critical path**.

**Why it is a distributed monolith:** Latency and failure modes multiply; you did not gain independent deployability—only network hops.

**Mitigation:** Move to **async events** for non-critical steps; keep **one** short synchronous boundary for checkout; use **sagas** with clear timeouts and compensations.

---

### 2. **Shared database with cross-context SQL joins**

**Red flag:** “Order service” and “Restaurant service” both query the same Postgres schema with **joins** across tables that belong to different contexts.

**Why it is a distributed monolith:** The database is still the **single coupling hub**; services cannot own their data or release independently.

**Mitigation:** **Database per service** (logical first): forbid cross-context joins; expose **read APIs** or **read models** built from events; use **strangler** slices to migrate data ownership gradually.

---

### 3. **Shared libraries that encode business rules for everyone**

**Red flag:** A single internal package `citybite-common` exports **entities + ORM models + validation** used by all services, forcing lockstep versioning.

**Why it is a distributed monolith:** Deployment independence is illusory—every service revs together when the shared library changes.

**Mitigation:** Replace with **versioned contracts** (OpenAPI/async schema), **consumer-driven contract tests**, and small **stable** shared primitives only (IDs, tracing, auth), not domain aggregates.

---

## Summary

Real microservices need **clear boundaries**, **owned data**, and **loosely coupled integration**. Without that, CityBite would only gain operational complexity—not flexibility.
