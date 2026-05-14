# Assignment Submission: Lecture 11

**Student Name**: Rajinish Chowdary Pothakamuri
**Student ID**:  30009056
**Submission Date**: 01-05-2026

## Overview

This submission documents a comprehensive availability and failure containment architecture for the CityBite platform, applying the principles from Chapter 11: Availability and Services. The design focuses on:

- Differentiating internal components from remote services and defining trust boundaries
- Establishing Service Level Objectives (SLOs) and Service Level Indicators (SLIs)
- Designing meaningful deep readiness and liveness probes for system monitoring
- Mitigating cascading failures utilizing circuit breakers, timeouts, and bulkheads
- Balancing data redundancy and the CAP theorem using synchronous and asynchronous replication
- Utilizing event sourcing for critical state recovery (Bonus)

## Files Included
```text
submissions/Rajinish_Pothakamuri/
├── part1_services_inventory.md
├── part1_slo_error_budget.md
├── part2_monitoring_probes.md
├── part2_cascading_failures.md
├── part3_replication_cap.md
├── part3_diagram_steady_vs_failure.drawio
├── part3_diagram_steady_vs_failure.png
├── part3_event_sourcing_bonus.md
└── README.md
```

## How to View

1. Open the `.drawio` file using draw.io (or the integrated Mermaid live editor) to view the editable architectural diagrams.
2. View the exported `.png` file for a quick visual reference of the steady versus failure states.
3. Read the `.md` files for the complete academic narrative and architectural documentation.
