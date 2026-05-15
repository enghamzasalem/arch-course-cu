# CityBite Flexibility and Microservices - Lecture 12

Analysis and design of a microservices migration strategy for CityBite, distributed monolith anti-patterns, database per service, API evolution, and a strangler fig migration plan.

## Files Included

- `part1_contexts_conway.md` – Three bounded contexts with ubiquitous language, integration styles, and Conway's Law prediction
- `part1_distributed_monolith.md` – Three distributed monolith red flags with mitigations
- `part2_database_per_service.md` – Logical schemas for two contexts, lost query replacement, and RPO/RTO intuition
- `part2_api_evolution.md` – Additive vs breaking changes for GET /orders/{id} with versioning and deprecation plan
- `part2_saga_sketch.md` – Choreography-based saga for place paid order with compensating actions
- `part3_strangler_plan.md` – Restaurant context extraction plan with facade, traffic ramp, rollback trigger, and branch by abstraction
- `part3_diagram_current_vs_target.drawio` + `.png` – Two-panel diagram: current monolith vs target bounded contexts with sync/async edges