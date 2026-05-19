# CityBite Scalability Architecture — Lecture 10

Analysis and design of a scalability architecture for CityBite, a regional food delivery platform. Covers workload modelling, bottleneck identification, scale-up vs scale-out decisions, data plane design, and autoscaling policy.

## Files Included

- `part1_workload_and_bottlenecks.md` - Five workload dimensions with first-saturating resources and a hero scenario
- `part1_scale_decisions.md` - Scale-up vs scale-out decision table for four subsystems
- `part2_data_scaling.md` - Write/read path design, Redis cache proposal, and queue-based notification decoupling
- `part2_architecture_steady_vs_peak.drawio` + `part2_architecture_steady_vs_peak.png` - Two-panel architecture diagram: steady vs peak with numbered flows and legend
- `part3_patterns.md` - Load balancing, sharding, scatter/gather, and master/worker mapped to CityBite
- `part3_autoscaling_and_limits.md` - HPA rule, backpressure policy, and failure lesson on scaling pods without the database