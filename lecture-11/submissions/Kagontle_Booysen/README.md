# Assignment Submission: Lecture 11

**Student Name**: Kagontle Booysen
**Student ID**: 30009255
**Submission Date**: 2026-04-30

## Overview

This submission documents how CityBite — a food-delivery platform running on Kubernetes and managed Postgres — stays available under dependency failures, traffic spikes, and misconfigured infrastructure. The work spans a services inventory and SLO design, a monitoring and failure-containment strategy, a replication and CAP analysis, a two-panel availability diagram, and an optional event-sourcing sketch. All designs reference the `example1_availability_circuit_breaker_citybite.py` and `example2_availability_monitoring_citybite.py` baselines from the lecture.

## Files Included

| File | Part / Task | Description |
|------|-------------|-------------|
| `part1_services_inventory.md` | Part 1 — Task 1.1 | Components vs external services table (8 rows); two SLA/exit-plan flags (Payment Gateway, Maps API); paragraph on why external API availability is a product risk |
| `part1_slo_error_budget.md` | Part 1 — Task 1.2 | SLI definition (checkout success ratio, latency-inclusive); SLO of 99.5 % over 30 days; error budget calculation and four-state burn-rate policy (Nominal → Elevated → Critical → Breached) |
| `part2_monitoring_probes.md` | Part 2 — Task 2.1 | Liveness vs readiness probe design for Order API; explanation of why shallow `/healthz` lies under pool exhaustion; external synthetic black-box probe spec; two Prometheus alert rules with thresholds and runbook first steps |
| `part2_cascading_failures.md` | Part 2 — Task 2.2 | Timestamped narrative of payment gateway 500 + retry storm cascade; circuit breaker policy (thresholds, open duration, half-open, tiered fallback); timeout hierarchy and bulkhead pool partitioning; canary request pattern applied to Dispatch Worker |
| `part3_replication_cap.md` | Part 3 — Task 3.1 | Sync vs async Postgres replica design (failover vs reporting); split-brain and stale-read failure scenarios; CAP trade-off analysis mapping each read path to AP or CP with consistency-consequence reasoning |
| `part3_diagram_steady_vs_failure.drawio` | Part 3 — Task 3.2 | Editable draw.io source — two-panel diagram: steady-state happy path (left) and gateway failure + circuit breaker + fallback path (right); numbered flows ①–④, legend, title block |
| `part3_diagram_steady_vs_failure.png` | Part 3 — Task 3.2 | Rendered 1700×1130 px export of the diagram for quick reference |
| `part3_event_sourcing_bonus.md` | Part 3 — Task 3.3 *(+8 bonus)* | Event sourcing sketch for the Order bounded context; 10-event list covering happy path and fallback states; concrete replay-after-bug scenario using compensating events and projection rebuild |

## Key Highlights

- **SLO tied to product outcomes** — the 99.5 % checkout SLO is deliberately set below what internal infrastructure can achieve so that external dependency degradation (gateway slowness, Maps API errors) counts against the budget and is owned by product leadership, not only SRE
- **Layered failure containment** — five mechanisms work in sequence: per-call timeout bounds individual cost → bulkhead bounds concurrent damage → circuit breaker prevents systemic amplification → tiered fallback (queue / decline) preserves UX → canary worker isolates novel payloads before they reach the main fleet
- **Replication matched to consequence** — sync replica (RPO = 0) for the order write path; async replica for ETA display and reporting; read-after-write routing to primary for the 2-second window after a user-visible state change; CAP choice is explicit and justified per read path
- **Event sourcing closes the recovery loop** — the `PAYMENT_PENDING` fallback from Part 2 creates an audit gap that event sourcing directly solves: replay identifies orders confirmed without a payment event, compensating events revert the projection, and the retry worker re-processes cleanly with a full immutable audit trail

## How to View

1. Open `.drawio` files in [draw.io](https://app.diagrams.net) to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files for documentation
4. Run code examples (if included) with Python 3
