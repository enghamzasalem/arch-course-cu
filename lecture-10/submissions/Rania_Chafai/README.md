# Assignment Submission: Lecture 10 - Scalability

## Student Information
- **Name:** Rania Chafai  
- **Submission Date:** 23/04/2026  

---

## Overview

This assignment presents a scalability architecture for **CityBite**, a regional food delivery platform. The design focuses on handling **traffic spikes** such as dinner rush and marketing campaigns by applying concepts from **Chapter 10: Scalability**.

The system builds on the Kubernetes-based architecture from Lecture 9 and introduces improvements to handle increased workloads efficiently.

---

## Key Concepts Applied

- Horizontal scaling using Kubernetes (HPA)
- Load balancing for distributing traffic
- Database optimization (primary + read replica)
- Caching to reduce repeated queries
- Asynchronous processing using queues and workers
- Identification and mitigation of bottlenecks

---

## Workload Context

CityBite experiences:
- High traffic during evening peak hours
- Sudden spikes during promotions
- Increasing number of restaurants and users
- High read load for menus and dashboards

The architecture addresses these challenges by scaling compute and optimizing data access paths.

---

## Architecture Highlights

### Steady State
- Limited number of API pods
- Direct reads from database
- Basic object storage for menu images
- Minimal background processing

### Peak State
- Autoscaled API pods using HPA
- Redis cache for menu data
- Read replica for scaling read operations
- Queue-based asynchronous processing
- Worker pool for notifications and background jobs

---

## Files Included

### Part 1: Workload and Bottlenecks
- `part1_workload_and_bottlenecks.md`
- `part1_scale_decisions.md`

### Part 2: Architecture Under Growth
- `part2_data_scaling.md`
- `part2_architecture_steady_vs_peak.drawio`
- `part2_architecture_steady_vs_peak.png`

### Part 3: Patterns and Operations
- `part3_patterns.md`
- `part3_autoscaling_and_limits.md`

---

## Design Decisions

- **Scale out** is preferred for stateless services (API, workers)
- **Scale up** is limited for the database, with read replicas added
- **Caching** reduces repeated database queries
- **Queues** decouple slow operations from user requests

---

## Limitations

- Database remains a potential bottleneck under extreme load
- Sharding is not implemented at this stage due to complexity
- Cache consistency may introduce slight staleness

---

## Conclusion

The proposed architecture improves scalability, performance, and resilience of CityBite under peak load conditions. It balances system complexity with practical scalability solutions suitable for real-world applications.

---

## Academic Integrity

This work is based on course materials from Lecture 10 and personal understanding of scalability concepts. Any external references would be cited if used.