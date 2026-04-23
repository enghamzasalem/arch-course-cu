# Part 3 — Scalability Patterns (CityBite)

## 1. Overview

CityBite uses a combination of architectural patterns to support growth, improve performance, and maintain fairness across multiple restaurants in a shared (multi-tenant) environment.

---

## 2. Load Balancing

CityBite relies on load balancing to distribute incoming traffic across multiple API pods running in Kubernetes. The Ingress controller ensures requests are spread evenly, so no single pod becomes a bottleneck.

During peak traffic, Horizontal Pod Autoscaling (HPA) increases the number of running pods, and the load balancer automatically distributes traffic across the expanded pool. This improves both availability and responsiveness.

Without load balancing, some pods would become overloaded while others remain underused, leading to poor system efficiency and inconsistent performance.

---

## 3. Sharding / Partitioning

To improve database performance, CityBite uses `restaurant_id` as a logical partition key. This ensures that queries for active orders only access the relevant subset of data instead of scanning the entire database.

As the system grows, this approach can evolve into full database sharding across multiple instances, potentially grouped by restaurant segments or regions. This improves scalability but also introduces operational complexity, so it is usually not necessary in early stages.

---

## 4. Scatter/Gather

The scatter/gather pattern is useful when combining data from multiple services, such as building a dashboard that includes orders, delivery status, and analytics.

In this approach, requests are sent to multiple services in parallel (scatter), and the results are combined before responding to the client (gather). While powerful, this approach can increase both latency and system complexity.

Because of this, CityBite only uses scatter/gather for non-critical features like analytics dashboards, and avoids it in the core checkout flow where low latency is essential.

---

## 5. Master/Worker (Worker Pool)

CityBite uses a worker pool model for background tasks such as sending notifications (SMS, email, push notifications).

In this setup:
- The API acts as the producer, publishing events to a queue  
- Worker pods consume these events and process them asynchronously  

This design decouples slow external operations from the main request cycle, improving responsiveness and overall throughput. Worker pools can also scale independently based on queue depth, making the system more flexible under load.

---

## 6. Multi-Tenant Fairness

Since CityBite serves multiple restaurants on the same infrastructure, fairness is an important concern.

To prevent one restaurant from impacting others:

- Heavy traffic from a single restaurant should not degrade system-wide performance  
- Partitioning by `restaurant_id` keeps queries scoped and efficient  
- Rate limiting and queue isolation help prevent resource starvation  

This ensures that even if one restaurant becomes extremely popular, it does not negatively affect others on the platform.