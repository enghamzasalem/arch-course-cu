# Task 1.1: Workload dimensions

As CityBite becomes more popular, there will be some specific measurable activities that consume resources such as:


| Dimension | Description | Primary Resource Saturated |
| :--- | :--- | :--- |
| **Concurrent Customers** | users are on the app at the same time looking at menus or tracking orders. | **RAM / Load Balancer Connections**: each active user keeps a connection open and uses memory. |
| **Orders per Minute (OPM)** | people are checking out every minute during busy times. | **DB IOPS / Disk Write Latency**: each order is a big transaction that hits Postgres hard. |
| **Menu Image Bytes** | image data we send when people load food photos. | **Network Egress**: sending lots of big images can clog the network. |
| **Dispatch Dashboard Queries** | Staff running heavy queries. | **DB CPU**: these big JOINs can slow down normal order queries. |
| **Notification Backlog** | The volume of SMS/Push messages are waiting to be sent. | **Application Locks / Queue Depth**: if workers fall behind, the queue fills up. |

## 1.2 Hero Scenario: The Friday Dinner Rush (19:00–21:00)
**Qualitative Description:**
* **Scaled Well:** Despite the 10x increase in traffic, the "Place Order" button responds in under 500ms. Kubernetes notices the extra load and automatically adds more API pods and the database stays stable because heavy dashboard queries go to a read replica, so the main DB can focus on writing new orders.
* **Scaled Poorly:** The main database hits 100% CPU because of slow queries and too many transactions. Users start seeing 504 Gateway Timeout errors when checking out and people refresh the app over and over, causing a Retry Storm.The connection pool gets overwhelmed and eventually the system enters a brownout, meaning almost nothing works and new orders can’t be processed.


