# Part 1 — Workload Model and Bottlenecks

## 1.1 Workload Dimensions

CityBite operates under dynamic and bursty workloads, especially during peak periods such as dinner rush hours and marketing campaigns. Scalability depends on understanding how these workloads grow and how they map to system resources.

| Workload Dimension    | Description                                         | Resource at Risk               |
| --------------------- | --------------------------------------------------- | ------------------------------ |
| Concurrent customers  | Number of users actively placing or tracking orders | CPU, network                   |
| Orders per minute     | Rate of incoming order requests                     | Database CPU, connections      |
| Restaurants onboarded | Number of restaurants using the platform            | Memory, database queries       |
| Menu image traffic    | Volume of images requested by users                 | Network bandwidth, storage I/O |
| Dashboard queries     | Real-time queries from restaurant dashboards        | Database reads, cache          |

---

## 1.2 Hero Scenario — Friday Dinner Rush

### Scenario:

During **Friday evening (19:00–21:00)**, CityBite experiences a peak workload with a high number of concurrent users placing orders simultaneously, often amplified by marketing campaigns.

### Well-Scaled System Behavior:

* Low and stable latency (p95 remains consistent)
* Orders processed reliably without duplication
* Restaurant dashboards update in near real-time
* System remains responsive under load
* Background operations (notifications, emails) are handled asynchronously

### Poorly-Scaled System Behavior:

* Increased latency and slow responses
* Database overload (CPU spikes, connection pool exhaustion)
* Failed or duplicated orders
* Dashboard lag and poor user experience
* Potential system downtime

---

## 1.3 Key Bottlenecks

### 1. Database (PostgreSQL)

* Single-writer architecture limits scalability
* High CPU usage during peak writes
* Connection pool exhaustion under heavy traffic
* Repeated queries for each restaurant increase load

### 2. Application Layer (Order API)

* CPU saturation under high concurrency
* Synchronous processing (e.g. notifications) increases latency

### 3. Hot Path Inefficiency

* Queries scanning global datasets instead of partitioned data
* Example: retrieving active orders without filtering by `restaurant_id`
* Leads to unnecessary work proportional to total system load

### 4. Network and Storage

* High bandwidth usage for menu images
* Disk I/O bottlenecks when accessing large datasets

---

## Conclusion

CityBite’s scalability challenges are primarily driven by database limitations, inefficient query patterns, and increasing concurrent workloads. Identifying bottlenecks in the hot path is essential to design scalable systems that can handle peak demand efficiently.
