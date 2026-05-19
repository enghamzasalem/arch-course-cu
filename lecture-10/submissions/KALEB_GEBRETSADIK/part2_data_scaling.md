# Part 2.1: Data Plane — Reads, Writes, Caches, and Queues

## 1. The Write Path: New Orders
When a customer creates a new order via the `POST /orders` API, the data flows as follows:
- **Strongly Consistent (Synchronous):** The payment authorization and the insertion of the order record into the primary PostgreSQL database are wrapped in a strictly ACID transaction. The database confirms the commit before a 200 OK HTTP response is returned to the user. This guarantees financial consistency so we never lose money or orders.
- **Eventually Consistent (Asynchronous):** Immediately after the database commit, the API pushes an "OrderCreated" event to an Outbox/Message Queue (e.g., RabbitMQ or SQS). Background notification workers consume this event to push a WebSocket alert to the restaurant's tablet and an email receipt to the customer. We **do not** block the customer's checkout HTTP response waiting for these external I/O notifications.

## 2. The Read Path: Kitchen Active Orders
Restaurants use their dispatch dashboard to constantly pull their unfulfilled orders.
- **Partition Key & Indexing:** As seen in the `example1_scalability_hot_path_citybite.py` narrative, querying the entire `orders` table linearly is a serial bottleneck. The read path heavily utilizes an index on `(restaurant_id, status)`. The `restaurant_id` serves as a natural logical partition key. When the API queries the DB, it acts as an extremely fast lookup against only that specific restaurant's subset of active orders, protecting the database CPU from full table scans.

## 3. Caching Strategy
- **Cache Target:** Active Restaurant Menus.
- **Key Structure:** `menu:restaurant:{restaurant_id}` stored in a distributed Redis cluster.
- **TTL & Invalidation:** Menus change infrequently. We set a long TTL (e.g., 24 hours). We utilize a write-through invalidation strategy: whenever a restaurant successfully updates their menu via the API, the system actively deletes/overwrites the `menu:restaurant:{restaurant_id}` key in Redis.
- **Stale Read Consequence:** If a customer views a stale menu (e.g., a dish just sold out but the cache hasn't cleared), they might add it to their cart. The system catches this at the checkout phase (which hits the strongly consistent database). The risk is a slightly annoyed user receiving a "Item no longer available" error, which is an acceptable UX trade-off to protect the database from millions of redundant menu reads.

## 4. Queues to Prevent Blocking
- Following the logic in `example2_scalability_queue_workers_citybite.py`, we would absolutely avoid blocking the HTTP checkout response for **fraud detection algorithms** and **delivery driver dispatching**. These are computationally expensive operations that often rely on slow 3rd-party mapping APIs. They run off a queue asynchronously after the core payment/order commit is confirmed.
