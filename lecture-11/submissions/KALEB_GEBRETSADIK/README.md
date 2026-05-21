# Assignment Submission: Lecture 11

**Student Name**: Kaleb Gebretsadik  
**Submission Date**: May 8, 2026

## Overview
This submission outlines the availability architecture for CityBite. It distinguishes internal components from external services, establishes SLOs/SLIs for checkout, defines liveness/readiness probes, mitigates cascading failures via circuit breakers and bulkheads, and details data redundancy and CAP theorem trade-offs.

## Files Included

- `part1_services_inventory.md`: Component vs services map, operators, and SLA requirements.
- `part1_slo_error_budget.md`: SLI/SLO and error budget definitions for checkout.
- `part2_monitoring_probes.md`: Liveness/Readiness probes and alerts/runbooks.
- `part2_cascading_failures.md`: Circuit breakers, timeouts, bulkheads, and canaries.
- `part3_replication_cap.md`: DB Sync vs Async replication, split-brain, and CAP tradeoffs.
- `part3_diagram_steady_vs_failure.drawio`: Visual diagram of steady vs fallback path.

## Key Highlights

- Addressed cascading failures from the payment gateway using circuit breakers.
- Designed fallback mechanisms (e.g., queuing "Pending" orders) instead of returning hard errors.
- Defined clear SLIs focusing on user journeys (checkout success rate) rather than purely system metrics.

## How to View

1. Open `.drawio` files in draw.io to see the editable diagram.
2. Read `.md` files for the core assignment documentation.
