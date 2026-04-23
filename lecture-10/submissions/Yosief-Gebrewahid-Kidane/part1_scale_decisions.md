# Part 1 — Scale Decisions (CityBite)

## 1. Overview

As CityBite grows and experiences higher demand—especially during peak hours like the dinner rush—it needs a clear strategy for scaling its system. This section looks at when it makes sense to scale **up (vertical scaling)** versus **out (horizontal scaling)** across different parts of the system.

---

## 2. Scale Decision Table

| Subsystem | Primary Bottleneck | Scale Up Option | Scale Out Option | Year 1 Choice | Justification |
|----------|------------------|----------------|------------------|--------------|--------------|
| Order API (Kubernetes Pods) | CPU, request throughput | Larger VM nodes | Increase number of pods (HPA) | Scale Out | The API is stateless, so scaling horizontally is straightforward, flexible, and cost-effective |
| Notification Workers | External I/O latency | Faster CPU (limited benefit) | More worker pods consuming queue | Scale Out | Tasks are independent and parallelizable, so adding more workers directly improves throughput |
| PostgreSQL (Primary DB) | CPU, connections, I/O | Larger instance (vertical scaling) | Read replicas, partitioning | Scale Up (initially) | Strong consistency requirements make vertical scaling simpler and more reliable in early stages |
| Object Storage / CDN | Network bandwidth, latency | Bigger instance (not typical) | Distributed CDN + storage scaling | Scale Out | Cloud storage systems are already designed to scale horizontally and handle global traffic efficiently |

---

## 3. Key Observations

A few clear patterns emerge from these decisions:

- **Stateless components** like the API and workers are much easier to scale horizontally  
- **Stateful systems**, especially databases, are more complex and often require vertical scaling first  
- **Managed cloud services** like object storage are built to scale out automatically  

---

## 4. Important Limitation

> The PostgreSQL primary database does **not scale infinitely**.

There are a few key constraints to keep in mind:

- It typically supports a **single writer**, which limits write scalability  
- Too many connections can lead to contention and degraded performance  
- Write-heavy workloads are difficult to distribute across multiple nodes  

### Mitigation Strategies

To address these limitations over time:

- Use **read replicas** to handle read-heavy workloads  
- Introduce **partitioning (sharding)** as the system grows  
- Add **caching layers** to reduce direct database load  