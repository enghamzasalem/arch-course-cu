# Assignment Submission: Lecture 10

**Student Name**: Amaan Shaikh

## Overview

This submission analyzes how CityBite handles increasing workload and scales under peak conditions. It covers workload dimensions, scaling decisions, data flow design, architecture differences between steady and peak load, and the use of common scalability patterns.

## Files Included

- `part1_workload_and_bottlenecks.md` — Workload dimensions, bottlenecks, and hero scenario
- `part1_scale_decisions.md` — Scale up vs scale out decisions for key subsystems
- `part2_data_scaling.md` — Data plane design including read/write paths, caching, and async processing
- `part2_architecture_steady_vs_peak.drawio` — Architecture diagram for steady vs peak load (draw.io)
- `part2_architecture_steady_vs_peak.png` — Architecture diagram for steady vs peak load (image)
- `part3_patterns.md` — Scalability pattern mapping for CityBite (load balancing, sharding, queues, multi-tenant fairness)
- `part3_autoscaling_and_limits.md` — HPA rule, backpressure strategy, and database scaling failure analysis
- `README.md` — This file

## Key Highlights

- Identified main bottlenecks such as database CPU and connection pool during peak traffic
- Designed a scalable data plane using Redis cache, read replicas, and SQS async workers
- Compared steady vs peak architecture with clear differences in replicas, cache usage, and queue depth
- Documented HPA rule (CPU 70%, min 3 / max 20 pods) and backpressure policy (503 Retry-After)
- Analyzed failure scenario: scaling API pods without scaling database makes the problem worse

## How to View

1. Open `.drawio` files in [draw.io](https://app.diagrams.net/) to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files in any text editor or Markdown viewer