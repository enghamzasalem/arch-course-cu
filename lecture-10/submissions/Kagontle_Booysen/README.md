# Assignment Submission: Lecture 10
**Student Name**: Kagontle Booysen
**Student ID**: 30009255
**Submission Date**: 21 April 2026

## Overview
This submission documents a scalability architecture for CityBite, a regional food delivery platform built on the Kubernetes baseline from Lectures 9–10. It applies Chapter 10 concepts — workload modelling, horizontal vs vertical scaling, bottleneck identification, caching, partitioning, autoscaling, and backpressure — to a dinner-rush and marketing-spike scenario. Five distinct scalability risks are addressed with concrete mechanisms: Postgres connection pool exhaustion, duplicate restaurant-polling queries, dashboard queries competing with OLTP writes, notification fan-out blocking checkout, and menu image egress latency.

## Files Included
- `part1_workload_and_bottlenecks.md` — Task 1.1: five workload dimensions, resource saturation mapping, and Friday 19:00–21:00 hero scenario (scaled well vs poorly)
- `part1_scale_decisions.md` — Task 1.2: scale up vs scale out decision log for five subsystems, including explicit Postgres single-writer "does not scale infinitely" note
- `part2_data_scaling.md` — Task 2.1: write path (ACID transaction + transactional outbox), read path (partition key + partial index), Redis cache design (key, TTL, invalidation strategy), and SQS async decoupling
- `part2_architecture_steady_vs_peak.drawio` — Task 2.2: editable two-panel draw.io diagram with 8 numbered flows, peak-only components highlighted, and legend
- `part2_architecture_steady_vs_peak.png` — Task 2.2: exported PNG for quick reference
- `part3_patterns.md` — Task 3.1: pattern checklist (load balancing, sharding/partitioning, scatter/gather, master/worker pool) with multi-tenant fairness notes and 5 Mermaid graph diagrams
- `part3_autoscaling_and_limits.md` — Task 3.2: HPA rule YAML with labelled assumptions, tiered backpressure/degradation policy (503 + Retry-After), and failure lesson on scaling pods while forgetting the database

## Key Highlights
- **Postgres is the serial bottleneck**: all five baseline risks trace to one Postgres instance; mitigated with PgBouncer, a read replica, a partial composite index on `(restaurant_id, status, created_at)`, and Redis caching that cuts DB read load by ~87% on the kitchen live-orders screen
- **Transactional outbox as the consistency boundary**: the only strongly-consistent unit is a three-row ACID transaction (`orders` + `order_items` + `outbox`); notifications, dispatch, and analytics are explicitly eventually consistent via autoscaled SQS workers, fully decoupling checkout latency from all outbound I/O
- **Autoscaling ceiling derived from downstream constraint**: `maxReplicas: 16` is calculated from PgBouncer's server pool (16 pods × 10 connections = 160 client connections multiplexed to 20–30 Postgres connections), so HPA can never inadvertently exhaust the database

## How to View
1. Open `.drawio` files in draw.io to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files for documentation
4. Mermaid code blocks in `part3_patterns.md` can be run in draw.io via Extras → Edit Diagram → switch to Mermaid
