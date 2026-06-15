## CityBite Availability Architecture — Lecture 11

Analysis and design of an availability architecture for CityBite, covering service dependencies, SLOs, monitoring probes, cascading failure containment, and data replication strategy.

### Files Included

- `part1_services_inventory.md` - Component vs external service inventory with SLA requirements and product risk paragraph
- `part1_slo_error_budget.md` - SLI, SLO, and error budget policy for the checkout user journey
- `part2_monitoring_probes.md` - Liveness vs readiness probes, synthetic check, and two alerting rules
- `part2_cascading_failures.md` - Retry storm narrative, circuit breaker policy, timeouts/bulkhead, and canary note
- `part3_replication_cap.md` - Sync vs async replication, split-brain risk, and CAP trade-off for read paths
- `part3_diagram_steady_vs_failure.drawio` + `png` - Two-panel checkout diagram: happy path vs gateway failure with circuit breaker fallback