# Assignment Submission: Lecture 11

**Student Name**: Arda Arslan  
**Student ID**: 30008610  
**Submission Date**: 06/05/2026

## Overview

This submission documents how CityBite stays available under failure. It covers components versus external services, SLOs and error budgets, monitoring and probes, cascading failures and the circuit breaker pattern, replication trade-offs and CAP, and an optional event sourcing sketch.

## Files Included

- `part1_services_inventory.md` - Components vs external services, SLA dependencies, and product risk
- `part1_slo_error_budget.md` - SLI, SLO, and error budget for the place paid order journey
- `part2_monitoring_probes.md` - Liveness vs readiness, synthetic check, and alerts
- `part2_cascading_failures.md` - Retry storm narrative, circuit breaker policy, timeouts, bulkhead, and canary
- `part3_replication_cap.md` - Sync vs async Postgres replication, split-brain, and CAP for ETA display
- `part3_diagram_steady_vs_failure.drawio` - Steady vs failure path diagram (draw.io)
- `part3_diagram_steady_vs_failure.png` - Steady vs failure path diagram (image)
- `part3_event_sourcing_bonus.md` - Bonus event sourcing sketch for order lifecycle
- `README.md` - This file

## Key Highlights

- Mapped CityBite dependencies and identified two services that need a formal SLA and exit plan
- Defined a measurable SLI based on final order state, not just HTTP responses, with a 99.5% monthly SLO
- Explained how retry storms cause cascading failures and how circuit breaker, timeouts, and bulkhead together contain them
- Compared steady and failure paths in one diagram, showing the breaker open state and the pay later fallback

## How to View

1. Open `.drawio` files in draw.io to see editable diagrams  
2. View `.png` files for quick reference  
3. Read `.md` files for documentation