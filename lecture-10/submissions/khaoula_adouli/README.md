# Assignment Submission: Lecture 10 — CityBite Scalability

**Student Name**: Khaoula Adouli  
**Submission Date**: 20/04/2026

---

## Overview

This submission presents a scalability architecture for the CityBite system under both steady and peak load conditions.  
It applies concepts from Chapter 10, including workload analysis, horizontal scaling, caching, queue-based decoupling, and database optimization strategies.

---

## Files Included

- `part1_workload_and_bottlenecks.md` — workload dimensions and bottleneck analysis  
- `part1_scale_decisions.md` — scale up vs scale out decisions  
- `part2_data_scaling.md` — read/write paths, caching, and queue design  
- `part2_architecture_steady_vs_peak.drawio` — editable architecture diagram  
- `part2_architecture_steady_vs_peak.png` — exported diagram image  
- `part3_patterns.md` — architectural patterns and trade-offs  
- `part3_autoscaling_and_limits.md` — autoscaling, backpressure, and failure analysis  

---

## Key Highlights

- Separation of **steady vs peak load behavior**
- Use of **Redis caching** to reduce database load during peak traffic
- **Read replica** to offload read-heavy queries (e.g. kitchen dashboard)
- **Queue + worker pattern** to decouple HTTP requests from notification delivery
- **Horizontal scaling (HPA)** applied to API pods and background workers

---

## Architecture Notes

The architecture follows the terminology used in lecture examples:

- Hot path optimization and indexing strategy  
- Partition-aware data access (restaurant-based access patterns)  
- Asynchronous processing using queue + workers  
- Clear separation of synchronous (blocking) and asynchronous flows  

---

## AI and Sources Disclosure

AI tools were used to assist with structuring and refining documentation.  
All technical decisions and claims were verified against lecture materials and relevant official documentation referenced in `part3_autoscaling_and_limits.md`.

---

## How to View

1. Open `.drawio` file in draw.io to view/edit the diagram  
2. View `.png` file for a quick visual overview  
3. Read `.md` files for detailed explanations  