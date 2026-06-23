## Part 1: Workload Model and Bottlenecks

### Task 1.1: Workload Dimensions

To effectively scale **CityBite**, we must identify the specific dimensions of the workload that grow as the platform expands and map them to the physical or logical resources they exhaust.

| Workload Dimension             | Description                                                                            | Primary Resource Bottleneck                                                                                                 |
| :----------------------------- | :------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------- |
| **Concurrent Customers**       | The number of active users browsing menus and placing orders simultaneously.           | **Network Egress / DB Connections**: High traffic exhausts the available connection pool to the PostgreSQL instance.        |
| **Orders Per Minute**          | The velocity of checkout transactions during peak periods like the dinner rush.        | **Database CPU**: Intensive write operations for order persistence and transaction logging.                                 |
| **Restaurants Onboarded**      | The total number of restaurant entities managed in the system state.                   | **RAM (Memory)**: Larger datasets require more memory for indexing and caching active restaurant metadata.                  |
| **Menu Image Volume**          | The total size of high-resolution food images stored and served to customers.          | **Storage Throughput / Bandwidth**: Large requests for binary data can saturate object storage IOPS or network interfaces.  |
| **Dispatch Dashboard Queries** | Frequent requests from restaurant tablets and dispatchers to view active order status. | **Application CPU / DB Locks**: Scanning large tables for "active" statuses creates serial bottlenecks and lock contention. |

---

### Hero Scenario: Friday Dinner Rush (19:00–21:00)

This scenario represents the **saturation point** where CityBite faces its highest predictable peak.

#### Scaled Well (Linear Scalability)

In a well-scaled system, the **response time remains stable** even as the throughput of orders increases proportionally to the influx of customers.

* **Customer Experience:** Browsing is fast because menu data is retrieved from caches. Checkout is smooth because notification side-effects (SMS/Email) are decoupled via queues rather than handled synchronously.
* **Restaurant Experience:** The kitchen dashboard updates in near real-time because queries are optimized using `restaurant_id` as a partition key, enabling efficient lookups regardless of total system load.

#### Scaled Poorly (Overload)

When the system reaches its **capacity limit** without proper mitigation, it enters an unstable state.

* **Customer Experience:** Users experience **p95 latency spikes**, slow responses, and timeouts. Some requests fail with “503 Service Unavailable” errors due to exhausted database connections.
* **Restaurant Experience:** The kitchen dashboard becomes slow or unresponsive. Inefficient queries (e.g., full-table scans) drive database CPU usage to 100%, creating a hotspot that affects all restaurants. Repeated client refresh attempts further increase load, worsening the situation.
