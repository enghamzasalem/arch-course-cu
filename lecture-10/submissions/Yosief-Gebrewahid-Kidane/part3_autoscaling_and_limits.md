# Part 3 — Autoscaling and System Limits (CityBite)

## 1. Overview

CityBite experiences highly variable traffic, especially during dinner peaks and marketing campaigns. To handle this reliably, the system relies on autoscaling to adjust resources dynamically, while backpressure mechanisms help prevent overload and cascading failures.

---

## 2. HPA (Horizontal Pod Autoscaling) for Order API

CityBite uses Kubernetes Horizontal Pod Autoscaling (HPA) to scale API pods based on CPU utilization.

### Configuration (assumption-based):

- Metric: CPU utilization  
- Target: 70%  
- Minimum replicas: 3  
- Maximum replicas: 20  

### Behavior:

- When CPU usage exceeds 70%, new API pods are created automatically  
- When traffic decreases, excess pods are gradually removed  
- Incoming requests are distributed through Kubernetes Service load balancing  

---

## 3. Backpressure and Degradation Strategy

When downstream systems become overloaded (for example, due to database stress or queue buildup), CityBite applies controlled degradation instead of allowing full system failure.

### Strategies:

- **Queue-based backpressure**
  - Limit queue size to prevent memory pressure  
  - Incoming work is buffered instead of immediately processed or dropped  

- **HTTP-level protection**
  - Return `503 Service Unavailable` with a `Retry-After` header when the system is saturated  

- **Feature degradation**
  - Temporarily disable non-critical features (e.g. recommendations, analytics updates)  
  - Prioritize core functionality like order creation  

---

## 4. Failure Scenario: Scaling Only the Application Layer

If only API pods are scaled while the database remains unchanged, several issues appear quickly.

### Symptoms:
- API throughput increases at first  
- Database connection count rises rapidly  
- Connection pool becomes exhausted  
- Query latency increases significantly  
- Eventually requests start timing out and returning 5xx errors  

---

### Detection:
Monitoring systems would typically show:
- High database CPU usage (close to 100%)  
- Increasing query latency  
- Rising error rates in application logs  

---

### Mitigation:
To stabilize the system:
- Introduce read replicas for read-heavy traffic  
- Optimize queries using indexes (e.g. `restaurant_id`)  
- Add caching layers (e.g. Redis) to reduce database pressure  
- Limit the number of DB connections per API pod  

---

## 5. Key Insight

Scaling only the stateless parts of the system (like API pods) is not enough. Real scalability requires balancing multiple layers:

- Compute scaling (application pods)  
- Data scaling (database design and optimization)  
- Asynchronous processing (queues and workers)  
- Controlled failure handling (backpressure and degradation)  

---

## 6. Final Principle

> A system is truly scalable only when it continues to behave predictably under stress, rather than failing abruptly when overloaded.