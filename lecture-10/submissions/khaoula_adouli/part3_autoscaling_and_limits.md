# Part 3.2 - Autoscaling and Backpressure

## 1) HPA proposal for Order API (assumptions)

Assumptions:
- Typical steady load: 120 RPS
- Peak campaign load: 450 RPS
- Pods request 500m CPU each

Proposed HPA rule:
- **Target metric:** CPU utilization (initially), target **65%** average
- **Replicas:** min **4**, max **24**
- **Scale-up behavior:** aggressive (short stabilization, e.g. 30s)
- **Scale-down behavior:** conservative (longer stabilization, e.g. 5 min)

Reasoning: CityBite has sharp dinner ramps; fast scale-up prevents p95 blowups. Slower scale-down avoids replica thrashing.

---

## 2) Backpressure / degradation policy

When DB or downstream queue is stressed:

1. If queue depth > threshold (example: 20,000 pending) then:
   - continue core order placement,
   - temporarily disable non-critical synchronous features,
   - return 202/accepted for optional side-effects where product allows.

2. If DB connection pool exhaustion is detected:
   - shed low-priority traffic (partner bulk sync first),
   - return **503 Service Unavailable** with **Retry-After**,
   - preserve checkout path budget for interactive users.

This keeps critical ordering available while protecting system recovery.

---

## 3) Failure lesson: scaling stateless pods without scaling DB

If CityBite only scales API pods, traffic handling appears improved initially but DB becomes the hard bottleneck. Symptoms include higher API pod count with worsening p95 latency, rising DB CPU, lock waits, and exhausted DB connections. Error rates increase (timeouts/5xx) even though Kubernetes shows many healthy API pods. Queue depth may also rise because workers cannot persist/read efficiently. Detection should include correlation dashboards: replica count vs DB CPU vs connection saturation vs latency. Mitigation requires DB-aware actions: query/index tuning, connection pool limits, read replicas for read-heavy paths, and cache for repetitive restaurant queries. In severe cases, apply admission control to reduce write pressure until DB recovers. The key lesson is that end-to-end scalability is constrained by the slowest serial resource, often the primary database.

---

## External references and academic notes

- Kubernetes HPA concepts: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ (accessed 2026-03-15)
- PostgreSQL performance basics: https://www.postgresql.org/docs/current/performance-tips.html (accessed 2026-03-15)

AI-use disclosure (per course policy): AI assistance was used for drafting structure and wording; technical claims were manually checked against lecture material and official docs above.
