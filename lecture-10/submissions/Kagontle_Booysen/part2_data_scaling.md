# Part 2 — Task 2.1: Data Plane — Reads, Writes, Caches
**CityBite Scalability Architecture | Lecture 10 Assignment**

---

## 2.1.1 Write Path — New Order

### End-to-end flow

```
Mobile customer                Order API pod               Postgres primary
──────────────    POST /orders  ──────────────  BEGIN TX   ─────────────────
  Checkout UI  ────────────────► Validate cart ────────────► INSERT orders
                                 Validate stock             INSERT order_items
                                 Charge payment             INSERT outbox
                                 (sync, Stripe)             COMMIT
                ◄────────────── HTTP 201 Created ◄──────────
                  (≤ 2 s SLA)

                                Outbox poller              SQS queue
                                (background)  ──────────►  "order.created"
                                                              │
                                                    ┌─────────┴──────────┐
                                                    ▼                    ▼
                                            Notification worker   Analytics worker
                                            (SMS / push)          (BI / dashboard)
```

### Consistency boundaries — what must be atomic

The following three writes **must succeed together or not at all** — they form a single ACID transaction on the Postgres primary:

| Write | Table | Why strongly consistent |
|---|---|---|
| Create order record | `orders` | The order must exist before any downstream system references it |
| Create order line items | `order_items` | Financial and fulfilment correctness — partial line items must never be visible |
| Append outbox event | `outbox` | Transactional outbox pattern: the event is durably recorded in the same commit as the order; the poller can only read it after the order row exists, so downstream consumers never see an event for an order that rolled back |

If the `COMMIT` fails for any reason (DB crash, network partition), all three writes are rolled back atomically. The customer sees a failure response and can safely retry.

### What can be eventually consistent

| Downstream concern | Mechanism | Acceptable lag | Risk of stale / delayed |
|---|---|---|---|
| Customer push / SMS notification | SQS → notification worker | 5–30 s | Low: a delayed "order confirmed" message is annoying but not incorrect; no financial or inventory consequence |
| Restaurant tablet new-order alert | SQS → restaurant polling or WebSocket push | 3–10 s | Low: restaurant staff have a 10–15 min preparation window; a few seconds of lag is invisible |
| Analytics / BI dashboard | SQS → analytics worker → data warehouse | Minutes to hours | Low: revenue dashboards do not need real-time accuracy; eventual consistency here is by design |
| Rider dispatch assignment | SQS → dispatch worker | 10–60 s | Medium: longer lag delays pickup, but the order is already confirmed; idempotent retry is safe |

The key insight is that **only the financial transaction needs strong consistency**. Everything else is a reaction to an already-committed fact, which is exactly what the outbox event represents.

---

## 2.1.2 Read Path — Kitchen Active Orders

### The query that matters

The restaurant tablet polls (or subscribes via WebSocket) for its active orders:

```sql
SELECT o.id, o.status, o.created_at, oi.name, oi.quantity
FROM   orders o
JOIN   order_items oi ON oi.order_id = o.id
WHERE  o.restaurant_id = $1          -- partition key
  AND  o.status IN ('confirmed','preparing')
ORDER  BY o.created_at ASC;
```

### Why this query is the hot path

At peak, every active restaurant runs this query every 3–10 seconds. With 300 restaurants in one city, that is **30–100 queries per second** hitting the database on exactly this pattern — this is the "duplicate heavy queries per restaurant" pain point in the baseline.

### Index and partition key thinking (from `example1`)

`example1_scalability_hot_path_citybite.py` identifies `restaurant_id` as the natural **partition key** for the orders table. The index strategy follows directly:

```sql
-- Composite index: filters by restaurant, then status, then sorts by time
-- All three clauses in the query above are served from one index scan
CREATE INDEX idx_orders_restaurant_status_time
    ON orders (restaurant_id, status, created_at DESC)
    WHERE status IN ('confirmed', 'preparing');  -- partial index: only active orders
```

**Why a partial index?** The vast majority of rows in `orders` are in a terminal state (`delivered`, `cancelled`). A partial index that excludes terminal states is dramatically smaller, fits in the Postgres `shared_buffers` cache more easily, and has faster index scans because dead rows are never scanned.

### Read replica routing

This query is a pure read. It must **never run on the Postgres primary**. The application layer routes all restaurant-polling reads to a read replica:

```
Restaurant tablet ──► Order API pod ──► PgBouncer (read pool) ──► Postgres read replica
                                         (routes by query tag or separate DSN)
```

The primary is reserved exclusively for writes, satisfying the bottleneck separation decided in Task 1.2.

---

## 2.1.3 Cache Proposal — Restaurant Active-Order List

### Cache design

| Attribute | Value |
|---|---|
| **Cache technology** | Redis (same instance proposed in Task 1.2) |
| **Cache key** | `orders:active:{restaurant_id}` e.g. `orders:active:42` |
| **Cached value** | JSON-serialised list of active order summaries (same shape as the SQL result above) |
| **TTL** | 8 seconds — slightly longer than the restaurant tablet's polling interval (5 s), so most polls are served from cache |
| **Invalidation strategy** | Write-through on order state change: whenever an order for `restaurant_id=42` transitions state (`confirmed → preparing → ready`), the Order API (or outbox worker) calls `DEL orders:active:42`; the next poll rebuilds the cache from the read replica |

### What happens on a stale read

The TTL of 8 seconds means that in the worst case a restaurant tablet sees an order list that is up to 8 seconds old. This is acceptable because:

1. The tablet's UI already has a "pull to refresh" affordance.
2. The restaurant has a 10–15 minute preparation window per order — an 8-second delay does not affect fulfilment.
3. An order cannot be "lost" by a stale read; it will appear on the next cache rebuild at worst.

The one edge case that matters is **order cancellation by the customer**. If a cancellation arrives and the cache is not invalidated immediately, the kitchen may start preparing a cancelled order. Mitigation: the order cancellation handler explicitly calls `DEL orders:active:{restaurant_id}` synchronously before returning the cancellation confirmation to the customer, guaranteeing the stale window closes within the same request.

### Connected CityBite screen

This cache directly serves the **restaurant tablet "Live Orders" screen** — the primary operational screen for kitchen staff. Without caching, every 5-second poll is a database query. With caching:

- 300 restaurants × 12 polls/min = 3 600 DB queries/min reduced to ~450 DB queries/min (cache miss on TTL expiry only) — an **87 % reduction in read load on the database**.
- The kitchen screen's perceived responsiveness improves because Redis latency (< 1 ms) replaces Postgres query latency (5–20 ms under load).

### Secondary cache — customer menu screen

| Attribute | Value |
|---|---|
| **Cache key** | `menu:{restaurant_id}:{menu_version}` |
| **TTL** | 5 minutes (menus change rarely during service) |
| **Invalidation** | Explicit `DEL` when a restaurant manager publishes a menu update via the management API |
| **Connected screen** | Customer app "Browse Menu" — the first screen loaded before checkout; the highest-traffic read endpoint in the system |

---

## 2.1.4 Queue / Stream — Where Not to Block the HTTP Response

### Reference to `example2`

`example2_scalability_queue_workers_citybite.py` demonstrates the core principle: **the Order API HTTP handler commits the database transaction and enqueues the outbox event, then returns `HTTP 201` immediately.** It does not wait for notifications, dispatch assignment, or analytics ingestion to complete.

### Concrete non-blocking points in the CityBite write path

| Step | Sync or async | Justification |
|---|---|---|
| Validate cart + Stripe charge | **Sync** | Must confirm payment before the order is created; failure must be returned to the customer |
| `INSERT orders + order_items + outbox` | **Sync** | ACID transaction; must complete before HTTP 201 |
| **HTTP 201 returned to customer** | — | ← This is the cutoff point; everything below is async |
| Send push / SMS to customer | **Async (SQS)** | External API call; latency is variable (50–500 ms); blocking the HTTP response on this would directly inflate p95 latency |
| Alert restaurant tablet | **Async (SQS)** | Same rationale; also decouples the notification worker failure mode from the checkout success rate |
| Write to analytics / BI | **Async (SQS)** | Analytics writes are high-volume and can tolerate minutes of lag |
| Assign rider / dispatch | **Async (SQS)** | Rider assignment depends on availability which is a separate service; blocking checkout on it would couple two independent domains |

### Queue depth as a load signal

The SQS `ApproximateNumberOfMessagesVisible` metric doubles as a **backpressure signal**: if the notification worker cannot keep up during a marketing spike, the queue depth grows but the Order API throughput is unaffected. KEDA autoscales the notification worker Deployment in response to queue depth, as described in Task 1.2. This is the key architectural benefit of the decoupled design — the write path's SLA is insulated from the performance characteristics of every downstream consumer.

```
SQS queue depth ──► KEDA ScaledObject ──► Notification worker replicas
     (grows)                                    (scale out: 2 → 20 pods)
     (drains)                                   (scale in:  20 → 2 pods)
```

---

## Data Plane Summary

```
WRITE PATH (strongly consistent core)
  POST /orders ──► Validate + Charge (sync) ──► ACID TX {orders + outbox} ──► HTTP 201
                                                          │
                                               Outbox poller (async)
                                                          │
                                              SQS "order.created" event
                                         ┌────────────────┼───────────────┐
                                   Notify worker    Dispatch worker   Analytics worker
                               (eventually consistent across all three)

READ PATH (offloaded, cached)
  Kitchen tablet ──► Redis cache hit (< 1 ms) ──► Live Orders screen
                          │ miss
                          └──► Read replica (index scan on restaurant_id) ──► cache write
```

---

*Terminology aligned with `example1_scalability_hot_path_citybite.py` (hot path, partition key, composite index) and `example2_scalability_queue_workers_citybite.py` (outbox pattern, async worker decoupling).*
