## Part 2.1: Data Plane - Reads, Writes, Caches

This section explains how CityBite manages data flow and consistency as the system scales to handle peak demand.

### 1. Write Path: New Order

When a customer completes checkout, the data follows a path designed to ensure reliability without blocking the user interface.

* **API to Database (Primary):** The Order API writes the new order record to the PostgreSQL primary database. This operation must remain strongly consistent to ensure correct payments, accurate inventory, and prevention of duplicate orders.

* **Database to Queue (Event):** After the order is successfully stored, an "order confirmed" event is placed onto a queue. This event triggers side effects such as notifications and analytics updates.

* **Consistency Model:** The order record is strongly consistent, while downstream processes such as notifications and analytics are eventually consistent. The customer receives confirmation immediately, while notifications may arrive a few seconds later after being processed by workers.

---

### 2. Read Path: Kitchen Active Orders

To avoid performance issues as data volume grows, the read path for restaurant dashboards is optimized.

* **Partition Key Design:** Queries for kitchen dashboards are filtered using a partition key such as `restaurant_id`.

* **Indexing Strategy:** An index on `(restaurant_id, status)` ensures that only relevant rows are accessed. This avoids full-table scans and allows each restaurant to retrieve its active orders efficiently, even as the total number of orders increases.

---

### 3. Caching Strategy

To reduce load on PostgreSQL, a caching layer is used for frequently accessed data.

* **Cache Usage:** An in-memory store such as Redis is used to cache restaurant menus.

* **Key and TTL:** Cache keys follow the format `menu:{restaurant_id}` with a time to live of 30 minutes.

* **Invalidation:** Cache entries are invalidated when a restaurant updates menu items, such as price or availability.

* **Stale Data Impact:** In some cases, customers may see slightly outdated menu data. This is an acceptable trade-off to reduce database load during peak periods. Any inconsistencies are handled during the strongly consistent checkout process.

---

### 4. Queue and Asynchronous Processing

Following a queue-based architecture, the system avoids blocking critical user requests.

* **Non-blocking Design:** The HTTP response for checkout is not delayed by external services such as SMS or push notifications.

* **Processing Flow:** The API stores the order, sends a message to a queue such as SQS or RabbitMQ, and immediately returns a `201 Created` response to the client.

* **Scaling Benefit:** This approach allows the system to handle high request volumes even if external services are slow or temporarily unavailable, improving overall reliability and throughput.
