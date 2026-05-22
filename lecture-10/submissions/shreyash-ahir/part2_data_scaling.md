# Part 2.1 — Data Plane: Reads, Writes, Caches

## Write Path: New Order

### Sequence

```
1.  Client POST /orders → Order API pod
2.  API validates request (idempotency key check against Redis)
3.  API writes order + order_items inside a single DB transaction (PRIMARY)
4.  Transaction commits → API returns 201 to client
5.  API publishes OrderPlaced event to SQS queue (best-effort, after commit)
6.  Notification worker dequeues OrderPlaced → calls push/SMS API
7.  Analytics writer dequeues OrderPlaced → appends to analytics DB / data warehouse
```

### What must be strongly consistent

- Steps 1–4: the write to the OLTP primary must be strongly consistent. The customer
  must not see a 201 unless the order is durably persisted. The kitchen must not miss
  an order. This is the core business invariant.
- Idempotency key check: must be atomic with the order write to prevent duplicate
  orders on client retry. Implemented as a `unique` constraint on `(idempotency_key)`
  with a `ON CONFLICT DO NOTHING` guard.

### What can be eventually consistent

- Notification delivery: a push notification arriving 5 seconds after the commit is
  acceptable. If the notification worker is temporarily down, orders are not lost —
  they queue up and drain when the worker recovers (example2 queue pattern).
- Analytics: the analytics DB can lag by seconds to minutes without affecting
  customer or kitchen experience.
- Read replicas: the kitchen dashboard reading from a replica with 100–500 ms
  replication lag is acceptable — a chef seeing an order one second after it was placed
  is fine.

---

## Read Path: Kitchen Active Orders

### The hot-path query (example1 alignment)

```sql
SELECT id, customer_name, items, status, created_at
FROM orders
WHERE restaurant_id = $1
  AND status IN ('placed', 'preparing')
ORDER BY created_at ASC;
```

**Partition key / index design:**  
- Composite index on `(restaurant_id, status, created_at)` — the `restaurant_id` is
  the partition key that eliminates the full table scan.  
- At higher scale: range-partition the `orders` table by `created_at` month, so old
  historical orders are in separate physical partitions that the active-orders query
  never touches.

**Direction of traffic:**  
This query runs on a **read replica**. The replica handles dashboard polling (every 5–10s
per tablet) without loading the write primary. The partition key ensures the query is an
Index Scan, not a Seq Scan, even with millions of rows.

---

## Cache: Restaurant Menu

### What is cached

- **Key:** `menu:{restaurant_id}` (Redis hash or JSON blob)
- **Value:** Full menu payload as served by `GET /restaurants/:id/menu`
- **TTL:** 60 seconds passive expiry
- **Invalidation:** Active invalidation on menu update — when a restaurant admin saves
  a menu change, the API calls `DEL menu:{restaurant_id}` before returning 200.
  The next request rebuilds the cache from the DB.

### Where this appears in the product

This cache directly addresses the **customer menu browse screen**: when a customer
taps a restaurant, the app fetches the menu. During dinner rush, hundreds of customers
may browse the same popular restaurant within seconds of each other. Without the cache,
each fetch issues the same PostgreSQL query. With Redis, only the first request (or the
first after TTL expiry) hits the DB; all others return in < 5 ms.

### What happens on stale read

A 60-second TTL means a customer could see a menu item as available for up to 60
seconds after it has been marked out-of-stock by the restaurant. This is acceptable:
the order validation at write time checks current availability, so the customer receives a
clear error at checkout if the item is actually unavailable. The cache serves the
browsing experience; correctness is enforced at the write path.

---

## Queue: Decoupling Checkout from Outbound I/O (example2 alignment)

The HTTP response for `POST /orders` must not block on:

- Sending push notifications (external API, latency variable, may rate-limit)
- Sending SMS confirmation (Twilio or equivalent, 200–800 ms per call)
- Writing to the analytics warehouse (batch ingest, not time-critical)
- Triggering restaurant alert sound on tablet (WebSocket push, separate service)

All four are dispatched by publishing an `OrderPlaced` message to an SQS queue
immediately after the DB commit. The HTTP response returns to the customer
within the time of the DB write only (typically 20–50 ms). Workers consume the
queue asynchronously and fan out to each downstream system independently.

This decoupling has a concrete reliability benefit: if the SMS provider is slow for
30 seconds, the customer still gets their 201 in 50 ms. The notification simply
arrives 30 seconds later — acceptable to the user, invisible to the API.
