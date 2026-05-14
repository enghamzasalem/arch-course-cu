# Assignment Submission: Lecture 12

**Student Name**: Rania Chafai
**Student ID**:30009596
**Submission Date**: 14/05/2026

# CityBite Split with Care — Flexibility & Microservices

## Project Overview

This project documents how CityBite can evolve from a monolithic architecture toward a more flexible microservices-oriented design.

The assignment focuses on bounded contexts, Conway’s Law, database-per-service design, API evolution, saga patterns, and incremental migration strategies such as strangler fig and branch by abstraction.

The goal is to improve flexibility and team autonomy while avoiding distributed monolith anti-patterns.

---

## Files Included

### `part1_contexts_conway.md`
Definition of bounded contexts, ubiquitous language, integration styles, and Conway’s Law analysis.

### `part1_distributed_monolith.md`
Analysis of distributed monolith anti-patterns and proposed mitigations.

### `part2_database_per_service.md`
Database-per-service design, query replacement strategies, and replication considerations.

### `part2_api_evolution.md`
Public API evolution rules including additive changes, breaking changes, and versioning strategy.

### `part2_saga_sketch.md`
Saga workflow for cross-context business operations with compensating actions.

### `part3_strangler_plan.md`
Incremental migration plan using strangler fig and branch-by-abstraction patterns.

### `part3_contexts_current_vs_target.drawio`
Editable architecture diagram showing current monolith vs target bounded-context architecture.

### `part3_contexts_current_vs_target.png`
Exported visual version of the architecture diagram.

### `README.md`
Summary of the assignment and architectural decisions.

---

## Key Highlights

- Clear separation of bounded contexts
- Database-per-service architecture
- Use of synchronous APIs and asynchronous events
- Saga-based coordination without distributed transactions
- API versioning and backward compatibility strategy
- Incremental migration using strangler fig pattern
- Identification of distributed monolith risks
- Event-driven communication through queues/events

---

## How to View

- Open `.drawio` files using draw.io for editable diagrams
- Use `.png` files for quick visualization
- Read `.md` files for detailed architectural explanations