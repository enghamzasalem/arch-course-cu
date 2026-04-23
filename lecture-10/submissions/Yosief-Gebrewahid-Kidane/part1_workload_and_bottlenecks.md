# Part 1 — Workload Model and Bottlenecks (CityBite)

## 1. Overview

CityBite handles a wide range of workloads that change throughout the day. Traffic increases during peak hours like the dinner rush and can spike even further during marketing campaigns. To design a system that scales reliably, it’s important to understand what grows over time and which resources are most likely to become bottlenecks.

---

## 2. Workload Dimensions and Resource Mapping

| Workload Dimension | Description | Resource Likely to Saturate |
|-------------------|------------|-----------------------------|
| Concurrent customers | Number of users browsing and placing orders at the same time | CPU (API pods), network |
| Orders per minute | Rate of incoming orders, especially during peak periods | Database CPU, DB connections |
| Restaurants onboarded | Growth in the number of restaurant partners using the platform | Memory (caches), DB indexing efficiency |
| Menu image traffic | Uploading and fetching menu images | Network egress, object storage throughput |
| Dispatch dashboard queries | Real-time queries from restaurant tablets | Database CPU, query latency |
| Notification events | Push notifications, emails, and SMS per order | External API latency, worker throughput |

---

## 3. Bottleneck Observations

Looking at these workloads, a few key bottlenecks stand out:

- The **database is the most critical pressure point**, mainly because:
  - It handles both high write volume (new orders)
  - It serves repeated read queries (e.g., restaurant dashboards)

- **Connection pool exhaustion** can happen when too many API pods try to connect to the database at once  

- **Duplicate queries** (for example, dashboards polling frequently) can unnecessarily increase load  

- **External services** like notification providers can slow down the system if they are handled synchronously  

---

## 4. Hero Scenario: Friday Dinner Rush (19:00–21:00)

This scenario represents peak demand, where the system is under maximum stress.

### If the system scales well:
- Customers experience fast and smooth checkout (e.g., <200ms API latency)  
- Restaurants receive near real-time updates on incoming orders  
- Notifications may be slightly delayed but are delivered reliably  
- The system remains stable with no visible downtime  

### If the system scales poorly:
- Checkout becomes slow or fails due to timeouts  
- Restaurants see delayed or inconsistent order updates  
- Database CPU usage spikes toward 100%  
- Error rates increase (timeouts, failed requests)  
- In worst cases, orders may be duplicated or lost  