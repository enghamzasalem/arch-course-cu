# Part 2.1 - Data Plane Under Growth (Reads, Writes, Caches)

## 1) Write path for new order

1. Mobile/Web -> Ingress -> Order API receives checkout.
2. API validates cart, restaurant status, and user/payment assumptions.
3. API writes order transaction to **Postgres primary** (strong consistency boundary).
4. API writes an **outbox event** in same transaction (`order_created`).
5. API returns order confirmation to client quickly.
6. Background worker reads outbox/queue and performs notifications + analytics updates.

### Strongly consistent vs eventually consistent

**Strongly consistent (must be immediate):**
- Order row creation, status transition invariants, idempotency key handling, payment/authorization linkage.

**Eventually consistent (can lag):**
- Push/SMS/email notifications, restaurant analytics counters, campaign attribution dashboards.

---

## 2) Read path for kitchen active orders (hot path)

- Kitchen tablet asks for active orders by restaurant.
- Query pattern should be bounded by restaurant partition key, not global table scan.
- Use index/partition-friendly filter: `restaurant_id + status + created_at`.
- Read from cache first for recent active set, fallback to DB (primary/replica policy by freshness need).

Representative SQL pattern:

```sql
SELECT id, restaurant_id, status, created_at, customer_note
FROM orders
WHERE restaurant_id = $1
  AND status IN ('PLACED', 'COOKING', 'READY')
ORDER BY created_at DESC
LIMIT 100;
```

This reflects the lecture hot-path idea: work scales with per-restaurant load, not total platform size.

---

## 3) Cache proposal (real screen)

### Cache target
- **Screen:** Restaurant kitchen "Active Orders" list.
- **Key:** `active_orders:{restaurant_id}:v1`
- **TTL:** 10-20 seconds
- **Invalidation:** On order status change event for that restaurant, invalidate key immediately.

### Stale-read behavior
- If cache is stale briefly, kitchen may see 1-2 recent updates delayed by seconds.
- Safety rule: critical actions (accept/mark ready) always validate against DB transaction state.

---

## 4) Queue/stream usage (where not to block HTTP)

Do **not** block checkout response on outbound I/O:
- Push notification calls
- SMS/email provider calls
- Non-critical webhooks
- Analytics/event export

Use queue + autoscaled worker pool (as in lecture example2). HTTP path should finish after durable order + outbox/queue enqueue.

---

## 5) Four concrete scalability risk mitigations

1. **DB read pressure:** read replica + query/index optimization for active orders.
2. **Hot repeated reads:** Redis cache with short TTL + event invalidation.
3. **Outbound dependency latency:** queue and worker pool for notifications.
4. **Peak API burst:** HPA scale-out + request budget and backpressure.
