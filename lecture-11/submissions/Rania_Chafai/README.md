## Assignment Submission: Lecture 11  
**Student Name:** Rania Chafai  
**Submission Date:** 29/04/2026  

---

## CityBite Always Open: Availability & Services  

### Project Overview  
This project documents how **CityBite ensures high availability** under real-world conditions such as partner failures, network issues, and high traffic scenarios.

Building on the Kubernetes and scalability architecture from previous lectures, this assignment focuses on:
- Service dependencies and trust boundaries
- Monitoring and system health
- Failure containment strategies
- Replication and consistency trade-offs

The goal is to ensure that CityBite remains **operational and resilient**, even when external services or internal components fail.

---

### Files Included  

- **part1_services_inventory.md**  
  Identification of system components vs external services and their associated risks.

- **part1_slo_error_budget.md**  
  Definition of SLI, SLO, and error budget for a critical user journey.

- **part2_monitoring_probes.md**  
  Description of liveness and readiness probes, monitoring strategy, and alerting.

- **part2_cascading_failures.md**  
  Analysis of cascading failures and implementation of circuit breaker and retry strategies.

- **part3_replication_cap.md**  
  Explanation of database replication strategies and consistency vs availability trade-offs.

- **part3_diagram_steady_vs_failure.drawio**  
  Editable architecture diagram.

- **part3_diagram_steady_vs_failure.png**  
  Visual representation of system behavior under normal and failure conditions.

- **part3_event_sourcing_bonus.md (optional)**  
  Optional bonus explaining how event sourcing can improve recovery and auditing.

---

### Key Highlights  

- Clear separation between **internal components** and **external services**
- Definition of measurable **availability (SLO/SLI)**
- Use of **circuit breaker** to prevent cascading failures
- Implementation of **timeouts and retries control**
- Monitoring strategy aligned with **real user experience**
- Use of **replication** to improve availability
- Understanding of **CAP trade-offs** in distributed systems

---

### Conclusion  

This design ensures that CityBite can remain available and stable even during failures.  
It focuses on limiting the impact of failures, improving observability, and maintaining a good user experience.

---