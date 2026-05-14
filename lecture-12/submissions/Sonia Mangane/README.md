# Lecture 12 Assignment — CityBite Split with Care: Flexibility & Microservices

## Overview

This submission documents how CityBite could evolve from its current monolith toward bounded-context services without creating a distributed monolith. It covers Conway's Law, database per service, API evolution rules, a saga sketch for the checkout journey, and a strangler fig migration plan for the Payment context.

All deliverables align with the vocabulary and patterns from:
- `example1_flexibility_coupling_citybite.py` — tight coupling vs ports/adapters (`PaymentPort`, `StripePaymentAdapter`)
- `example2_flexibility_api_evolution_citybite.py` — additive vs breaking JSON changes, v1/v2 versioning

---

## Files Included

| File | Part | Description |
|------|------|-------------|
| `part1_contexts_conway.md` | 1.1 | Five bounded contexts with ubiquitous language, integration styles between each pair, Conway's Law prediction for a single-team setup |
| `part1_distributed_monolith.md` | 1.2 | Three red flags for a distributed monolith (sync chains, shared DB, deployment lockstep) with one mitigation each |
| `part2_database_per_service.md` | 2.1 | Logical schemas for Ordering and Dispatch contexts, lost query replaced by event-driven read model, RPO/RTO intuition for async replication |
| `part2_api_evolution.md` | 2.2 | Two additive changes and one breaking change for `GET /orders/{id}`, URL versioning + deprecation window, consumer-driven contract tests (Pact) |
| `part2_saga_sketch.md` | 2.3 | Choreography saga for "place paid order" across Ordering, Payment, and Dispatch — local steps, compensating actions, pros/cons of choreography |
| `part3_strangler_plan.md` | 3.1 | Payment context extracted first — facade/gateway ramp plan, rollback triggers, branch by abstraction using `PaymentPort` from `example1` |
| `part3_contexts_current_vs_target.drawio` | 3.2 | draw.io diagram — left: current monolith with shared DB; right: target bounded contexts with async event bus and DB per service |
| `part3_contexts_current_vs_target.png` | 3.2 | PNG export of the diagram *(export from draw.io)* |

---

## Flexibility Mechanisms Named (≥ 4 required)

1. **Strangler fig / facade** — incremental extraction of Payment behind an API Gateway with traffic % ramp
2. **Branch by abstraction** — `PaymentPort` interface introduced in the monolith before any split, enabling safe coexistence of old and new implementations
3. **Database per service** — Ordering and Dispatch own separate schemas; no cross-context SQL joins
4. **Saga (choreography)** — cross-context checkout flow without distributed 2PC
5. **Consumer-driven contract tests (Pact)** — automated detection of breaking API changes before deployment

## Explicit Trade-off

**Flexibility vs consistency:** Splitting databases per service eliminates the shared-schema coupling that slows teams, but the operations dashboard query that previously joined `orders` and `deliveries` in a single SQL statement must be replaced by an event-driven read model. This read model is **eventually consistent** — it may lag by up to ~1 second. The trade-off is accepted because the operations dashboard does not require real-time accuracy, and the decoupling benefit (independent deployability, independent scaling, independent failure domains) outweighs the staleness cost.

---




