# Lecture 11 Assignment — CityBite Always Open: Availability & Services

## Overview

This submission documents how CityBite (the fictional food delivery platform from Lectures 9–11) achieves and maintains availability. It covers the full scope of the assignment: mapping owned components vs external dependencies, defining measurable SLOs, designing monitoring probes, containing cascading failures with circuit breakers, and reasoning about data replication trade-offs.

All deliverables align with the vocabulary and patterns from:
- `example1_availability_circuit_breaker_citybite.py` — circuit breaker states, retry storms, fail-fast
- `example2_availability_monitoring_citybite.py` — shallow vs deep health probes, pool exhaustion

---

## Files Included

| File | Part | Description |
|------|------|-------------|
| `part1_services_inventory.md` | 1.1 | Components vs external services table (8 entries), two dependencies requiring formal SLA/exit plan, paragraph on why external API availability is a product risk |
| `part1_slo_error_budget.md` | 1.2 | SLI definition for the "place a paid order" journey, SLO target (99.5% / 30 days), error budget calculation and burn-rate response table |
| `part2_monitoring_probes.md` | 2.1 | Liveness vs readiness probe design for the Order API, contrast with `example2` shallow health lie, synthetic black-box check, two alerts with thresholds and runbook first steps |
| `part2_cascading_failures.md` | 2.2 | Narrative of payment gateway 500 + retry storm, circuit breaker policy (thresholds, open duration, fallback UX), timeouts and bulkhead design, canary request use case |
| `part3_replication_cap.md` | 3.1 | Sync vs async Postgres replica (failover vs reporting), RPO intuition, split-brain risk, CAP trade-off (AP for ETA display, CP for payment path) |
| `part3_diagram_steady_vs_failure.drawio` | 3.2 | draw.io diagram — left panel: steady-state happy path checkout; right panel: gateway failure → breaker OPEN → async fallback queue. Numbered flows, legend, title block |
| `part3_diagram_steady_vs_failure.png` | 3.2 | PNG export of the diagram above *(to be exported from draw.io)* |
| `part3_event_sourcing_bonus.md` | 3.3 *(+8 bonus)* | Event sourcing sketch for the order lifecycle bounded context — events list, how replay recovers from a buggy projection without data loss |

---

## Availability Risks Addressed

The assignment required at least four distinct availability risks with named mechanisms. This submission covers:

1. **Retry storm from payment gateway failure** → Circuit breaker (fail-fast, OPEN state)
2. **Pod appears healthy but cannot serve** → Deep readiness probe (DB pool check)
3. **Cascading thread exhaustion** → Bulkhead (per-dependency connection limits) + timeouts
4. **Data loss on primary DB failure** → Synchronous replication with managed failover
5. **Stale reads after failover** → CP vs AP routing strategy per use case
6. **Anomalous / fraudulent order payloads crashing workers** → Canary request pattern




