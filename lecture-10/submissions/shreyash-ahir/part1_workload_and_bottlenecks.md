# Part 1.1 — Workload Dimensions and Bottlenecks

## Workload Dimensions

### 1. Concurrent customers placing orders

**What grows:** Number of simultaneous HTTP sessions from mobile app during dinner rush.  
**Resource that saturates first:** DB connection pool. Each order placement touches at least three tables (orders, order_items, restaurant_availability) inside a transaction. PostgreSQL has a fixed `max_connections` ceiling. At peak, API pods queue waiting for connections; p95 latency spikes before CPU does.  
**Measurement:** Requests per second (RPS) on `POST /orders`; active DB connections via `pg_stat_activity`; connection pool wait time (PgBouncer `cl_waiting`).

---

### 2. Restaurant menu read traffic

**What grows:** Every time a customer opens the app, the restaurant list and menu items are fetched. A marketing push that doubles active users doubles these reads instantly.  
**Resource that saturates first:** DB CPU and I/O, because menu queries are never cached in baseline. A single popular restaurant can generate thousands of identical queries per minute — the "duplicate heavy queries per restaurant" pain point.  
**Measurement:** `pg_stat_statements` top queries by total_time; QPS on `GET /restaurants/:id/menu`.

---

### 3. Active kitchen orders (dispatch dashboard reads)

**What grows:** Restaurant tablets and the dispatch dashboard poll for live order state continuously. Unlike customer reads, these queries filter by `restaurant_id` and `status = 'active'`, touching a high-churn partition of the orders table.  
**Resource that saturates first:** Index pressure and row-lock contention on the `orders` table as concurrent writers (API placing orders, workers updating status) compete with readers (dashboard polling).  
**Measurement:** `pg_locks` contention; mean query time on `SELECT ... WHERE restaurant_id = X AND status = 'active'`; dashboard perceived refresh latency.

---

### 4. Notification worker throughput (order confirmation, ETA, delivery alerts)

**What grows:** One outbound notification per order event times order volume. A campaign spike that 5x's order rate 5x's notification jobs. Each job calls external SMS/push APIs.  
**Resource that saturates first:** Worker pod count and external API rate limits. If notifications are dispatched synchronously on the HTTP path, the Order API becomes directly throttled by SMS latency.  
**Measurement:** Notification queue depth (SQS `ApproximateNumberOfMessagesVisible`); worker pod CPU; external API error rate (429s).

---

### 5. Menu image storage and egress

**What grows:** Number of onboarded restaurants times average images per menu item. Every customer app load fetches multiple images.  
**Resource that saturates first:** Network egress bandwidth and object store GET request rate. Serving images directly from origin during a campaign push can exhaust egress quotas.  
**Measurement:** Object storage GET request rate; CDN cache hit ratio; monthly egress bytes.

---

### 6. Restaurants onboarded (multi-tenant data growth)

**What grows:** Row count in `restaurants`, `menu_items`, `orders` grows monotonically.  
**Resource that saturates first:** Disk IOPS and sequential scan time on un-partitioned tables. Without table partitioning on `orders`, a `SELECT` for one restaurant must scan all historical rows.  
**Measurement:** Table bloat (`pg_relation_size`); autovacuum lag; query plan showing Seq Scan vs Index Scan.

---

## Hero Scenario: Friday 19:00–21:00, Amsterdam

**Scaled well:**  
A customer opens the app at 19:05. The restaurant list and menu load in under 400 ms because they are served from Redis cache. She places an order; the API returns 201 in under 300 ms. The kitchen tablet updates the order status within 2 seconds of the chef accepting it. She receives a push notification 10 seconds later confirming the order. The dispatch dashboard shows live ETA without lag. Latency is flat between 19:00 and 20:30 despite 4x the steady-state RPS.

**Scaled poorly:**  
The same customer sees a spinner for 6 seconds on the restaurant list because the menu query hits a saturated DB. When she submits the order, she gets a 504 timeout because the connection pool is exhausted — every API pod is waiting for a DB slot. The kitchen tablet shows stale order states because the dashboard query is queued behind active order writes. She retries the order and accidentally creates a duplicate. The notification arrives 4 minutes later, by which time she has already called the restaurant directly.
