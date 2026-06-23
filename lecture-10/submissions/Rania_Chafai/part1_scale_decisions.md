# Part 1 — Scale Up vs Scale Out Decisions

## 1.2 Scaling Decision Log

To handle increasing workload, CityBite must choose between **vertical scaling (scale up)** and **horizontal scaling (scale out)** depending on the subsystem and its bottlenecks.

| Subsystem                   | Primary Bottleneck                    | Scale Up Option                | Scale Out Option                  | Decision (Year 1)            | Justification                                                          |
| --------------------------- | ------------------------------------- | ------------------------------ | --------------------------------- | ---------------------------- | ---------------------------------------------------------------------- |
| Order API (Kubernetes pods) | CPU, concurrent requests              | Larger VM / more CPU per pod   | Add more pods (HPA)               | Scale Out                    | Stateless services scale easily with replicas and improve availability |
| Notification Workers        | I/O (external APIs), queue throughput | Bigger worker instance         | More workers consuming from queue | Scale Out                    | Parallel workers improve throughput and decouple workload using queues |
| PostgreSQL (Primary DB)     | CPU, connections, single-writer       | Larger instance (more CPU/RAM) | Read replicas (read scaling)      | Scale Up + Partial Scale Out | Writes require strong consistency, but reads can be distributed        |
| Object Storage / CDN        | Network bandwidth, latency            | Bigger storage node            | CDN distribution globally         | Scale Out                    | Content delivery is best handled via distributed caching (CDN)         |

---

## 1.3 Scalability Limits

Not all components can scale infinitely:

* **PostgreSQL Primary Database:**

  * Limited by **single-writer constraint**
  * Vertical scaling has physical and cost limits
  * High write throughput becomes a bottleneck under heavy load

* **Sharding Complexity:**

  * Partitioning data across multiple databases introduces complexity
  * Requires careful choice of partition keys (e.g. `restaurant_id`)
  * Impacts query design and data consistency

* **Operational Costs:**

  * Scaling out increases infrastructure cost
  * Requires monitoring, autoscaling policies, and orchestration

---

## Conclusion

CityBite benefits from **horizontal scaling** for stateless services such as APIs and workers, while the database requires a hybrid approach combining vertical scaling and read replicas. Understanding these trade-offs is essential to design a scalable system that balances performance, cost, and complexity.
