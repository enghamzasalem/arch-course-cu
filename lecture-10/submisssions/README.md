# Assignment Submission: Lecture 10

**Student Name**: Rajinish Pothakamuri
**Student ID**: 30009056
**Submission Date**: 24-04-2026

## Overview

This submission documents a comprehensive scalability architecture for **CityBite**, a regional food delivery platform. [cite_start]The design addresses the challenges of a centralized system during peak dinner rushes and marketing pushes by implementing horizontal scaling, asynchronous processing, and data partitioning strategies derived from Chapter 10 principles[cite: 1, 14].

## Files Included

- [cite_start]`part1_workload_and_bottlenecks.md`: Identification of workload dimensions (users, orders, data) and their corresponding hardware bottlenecks[cite: 215, 218].
- [cite_start]`part1_scale_decisions.md`: A decision log justifying scale-up vs. scale-out strategies for API pods, workers, and database components[cite: 196, 212].
- `part2_data_scaling.md`: Documentation of the write path, read path (indexed by restaurant), and caching strategies to maintain p95 latency.
- [cite_start]`part2_architecture_steady_vs_peak.drawio`: Editable diagram showing the architectural transition from normal load to peak saturation[cite: 28, 48].
- `part2_architecture_steady_vs_peak.png`: Exported visual reference of the CityBite scaling model.
- [cite_start]`part3_patterns.md`: Analysis of architectural patterns including Load Balancing, Sharding, and Master/Worker pools[cite: 14, 396].
- [cite_start]`part3_autoscaling_and_limits.md`: Configuration for Kubernetes HPA and backpressure policies to prevent cascading failures[cite: 38, 91].

## Key Highlights

- **Decoupled Workflows**: Utilizes a Master/Worker pattern to move non-critical I/O (notifications) out of the checkout request path, increasing throughput.
- **Optimized Hot Paths**: Implementation of indexing and partitioning by `restaurant_id` to ensure kitchen dashboards scale independently of global order volume.
- [cite_start]**Graceful Degradation**: Defined operational limits and backpressure strategies to maintain core functionality (ordering) when secondary systems saturate during peaks[cite: 93, 112].

## How to View

1. **Open `.drawio` files** in draw.io to see editable diagrams and architectural flows.
2. **View `.png` files** for a quick visual reference of the steady vs. peak state comparison.
3. **Read `.md` files** for detailed technical documentation and scalability justifications.
4. **Run code examples** (if referencing `example1` or `example2`) using Python 3 to verify benchmark results.