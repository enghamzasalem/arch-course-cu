## Task 2.1: Data Scaling

### Write Path - New Order

```
Customer → Order API → INSERT orders (Postgres primary) → return 200 to client
                                    └─► enqueue event (SQS / outbox)
                                                └─► notification-worker → push/SMS
                                                └─► analytics pipeline
```

**Strongly consistent:** the `INSERT` into the `orders` table. The customer must receive a confirmed order ID before the HTTP response returns.

**Eventually consistent:** push/SMS notifications and analytics writes. These are enqueued after the DB commit and processed by the notification worker asynchronously. A few seconds delay is acceptable; blocking the HTTP response on them is not.

---

### Read Path - Kitchen Active Orders

The kitchen dashboard calls `GET /restaurants/{id}/orders/active`.

Without an index, the query scans every order in the table regardless of restaurant, cost grows with global order volume, not with what this one restaurant needs. This is the `NaiveOrderBoard` problem from `example1`.

With an index on `(restaurant_id, status)`, the query touches only that restaurant's rows. Cost stays proportional to per-restaurant load. This is the `IndexedOrderBoard` fix. The same logic applies at the Postgres layer via a B-tree index rather than an in-memory dict.

---

### Cache - Restaurant Menu

| Property | Value |
|---|---|
| **Screen** | Customer browsing the menu |
| **Cache key** | `menu:{restaurant_id}` |
| **TTL** | 60 s |
| **Invalidation** | On restaurant menu save event, delete the key immediately |
| **On stale read** | Customer sees a menu up to 60 s old - acceptable; worst case an item is shown that was just 86'd, handled at checkout validation |

Menu data is read far more than it is written. Without a cache, every browse request hits Postgres. During a dinner rush with hundreds of concurrent customers, this is redundant identical queries on the primary for data that has not changed.

---

### Queue - Where Not to Block the HTTP Response

From `example2`, `checkout_synchronous` runs all outbound I/O (push, email) inside the request, so checkout latency includes every downstream call. `checkout_with_worker_pool` shows the fix, persist and enqueue, then return 200; workers drain the queue in parallel.

When applied to CityBite, after the `INSERT orders` commits, the Order API enqueues a lightweight event and responds immediately. The `notification-worker` Deployment picks up the event and calls the push/SMS gateway. The HTTP handler never waits on external I/O.