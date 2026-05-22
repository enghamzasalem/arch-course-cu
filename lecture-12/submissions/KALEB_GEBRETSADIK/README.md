# Assignment Submission: Lecture 12

**Student Name**: Kaleb Gebretsadik  
**Submission Date**: May 22, 2026

## Overview

This submission documents how CityBite can evolve toward bounded-context microservices without creating a distributed monolith. It covers context mapping, anti-patterns, database per service, API versioning, saga choreography, and a strangler fig migration plan for the Payment context.

## Files Included

| File | Description |
|---|---|
| `part1_contexts_conway.md` | 5 bounded contexts, integration styles, Conway's Law prediction |
| `part1_distributed_monolith.md` | 3 distributed monolith red flags and mitigations |
| `part2_database_per_service.md` | Separate schemas for Ordering and Payment, lost query replacement, RPO/RTO |
| `part2_api_evolution.md` | Additive vs breaking changes for `GET /orders/{id}`, versioning and contracts |
| `part2_saga_sketch.md` | Choreography saga for "Place Paid Order" with compensations |
| `part3_strangler_plan.md` | Strangler fig + branch by abstraction for Payment extraction |
| `part3_contexts_current_vs_target.drawio` | Architecture diagram: monolith → bounded contexts |

## Key Highlights

- Used ports/adapters (`PaymentPort` interface) as the seam for branch by abstraction, directly referencing `example1`.
- Showed additive JSON evolution from `example2` as the default API change strategy with URL-based v2 versioning for breaking changes.
- Chose **choreography** for the Place Order saga and justified the observability cost trade-off honestly.
- Identified shared database and synchronous call chains as the primary distributed monolith red flags.

## How to View

1. Open `.drawio` file in draw.io for the editable architecture diagram.
2. Read `.md` files for all assignment documentation.
