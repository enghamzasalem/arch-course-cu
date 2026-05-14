# Assignment Submission: Lecture 12

**Student Name**: Kagontle Booysen  
**Student ID**: 30009255 
**Submission Date**: 13 May 2026

---

## Overview

This submission addresses Chapter 12: Flexibility and Microservices, applied to the CityBite food-delivery case study. The assignment covers bounded context design, distributed monolith anti-patterns, database-per-service schemas, public API evolution rules, a saga sketch for the "place paid order" journey, and an incremental strangler-fig migration plan for the Payment context — all building on the Kubernetes + Postgres baseline from Lectures 9–11 and aligned with the vocabulary of `example1_flexibility_coupling_citybite.py` (ports/adapters) and `example2_flexibility_api_evolution_citybite.py` (additive vs breaking JSON change).

---

## Files Included

### Part 1 — Contexts & Conway's Law

| File | Description |
|---|---|
| `part1_contexts_conway.md` | Five bounded contexts with ubiquitous language, primary users, integration styles, and a Conway's Law paragraph |
| `part1_contexts_conway.docx` | Formatted Word version of the above with colour-coded context cards and integration style table |
| `part1_distributed_monolith.md` | Three distributed monolith red flags (shared DB, sync call chains, lockstep deployment) with one mitigation each |
| `part1_distributed_monolith.docx` | Formatted Word version with callout boxes and summary table |

### Part 2 — Data, APIs, Sagas

| File | Description |
|---|---|
| `part2_database_per_service.md` | Logical schemas for Ordering and Payment contexts; replacement for the lost cross-schema JOIN; RPO/RTO intuition for Payment under async replication |
| `part2_database_per_service.docx` | Formatted Word version with colour-coded schema cards and RPO/RTO summary table |
| `part2_api_evolution.md` | Two additive changes and one breaking change to `GET /orders/{id}`; URL versioning strategy; 90-day deprecation window; consumer-driven contract tests |
| `part2_api_evolution.docx` | Formatted Word version with JSON payload blocks, versioning rationale, and deprecation timeline table |
| `part2_saga_sketch.md` | Orchestrated saga for "place paid order" across Ordering, Payment, Dispatch, and Notifications; compensating actions; failure matrix; state machine; explicit trade-off |
| `part2_saga_sketch.docx` | Formatted Word version with step cards, failure matrix, and ASCII state machine |

### Part 3 — Migration & Diagram

| File | Description |
|---|---|
| `part3_strangler_plan.md` | Payment context chosen for first extraction; strangler plan (Phase 0 branch by abstraction → Phase 1 facade → Phase 2 canary ramp → Phase 3 cutover); four rollback triggers; three branch-by-abstraction steps tied to `example1` |
| `part3_strangler_plan.docx` | Formatted Word version with phase cards, ramp schedule table, rollback trigger table, and annotated code blocks |
| `part3_contexts_current_vs_target.drawio` | Editable draw.io diagram — left: current shared-schema monolith; right: target bounded contexts with labelled sync/async edges, numbered flows, legend, and title block |
| `part3_contexts_current_vs_target.png` | Exported PNG of the above for quick reference |

---

## Key Highlights

- **Four distinct flexibility mechanisms** named and applied throughout: strangler fig (Part 3), database-per-service (Part 2.1), saga with compensating transactions (Part 2.3), and consumer-driven contract tests (Part 2.2) — satisfying the assignment's minimum-four requirement
- **`example1` port/adapter pattern carried through all parts**: `PaymentPort` / `OrderServiceLoose` is the basis for the distributed monolith mitigation (Part 1.2), the saga's Step 2 gateway call (Part 2.3), and all three branch-by-abstraction code steps in the strangler plan (Part 3.1)
- **`example2` additive vs breaking JSON rules applied directly**: `order_v1_additive` and `order_v2_breaking_rename` are cited by function name in Part 2.2, with the `simulate_old_client` tolerant-reader guarantee used to justify both additive changes
- **One explicit trade-off stated**: eventual consistency (flexibility gained) vs distributed two-phase commit (hard consistency rejected) in the saga — Part 2.3, with latency and ops cost implications linked to Lecture 10 and 11 baselines
- **Strangler plan is non-destructive**: the `HttpPaymentAdapter` is merged dark before any traffic shifts; rollback at every phase is a single DI configuration change or feature flag reset, never a redeployment

---

## How to View

1. Open `.drawio` files in [draw.io](https://app.diagrams.net) (desktop or web) to see the fully editable current-vs-target architecture diagram with all labelled edges and context boundaries
2. View `.png` files for a quick-reference version of the same diagram without opening draw.io
3. Read `.md` files for the full documentation — all cross-references between tasks (e.g. Part 1.1 integration styles referenced in Part 2.3 saga, Task 2.1 RPO section referenced in Part 3.1 rollback triggers) are resolved within the markdown
4. The `.docx` files contain the same content as the `.md` files in formatted Word layout — open in Microsoft Word or LibreOffice Writer; no additional fonts or plugins required
5. Run the provided course examples with Python 3 to verify the port/adapter and API evolution patterns this submission references: `python3 example1_flexibility_coupling_citybite.py` and `python3 example2_flexibility_api_evolution_citybite.py`
