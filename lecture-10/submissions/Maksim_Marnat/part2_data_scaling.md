# Part 2.1 — Data plane: writes, reads, cache, and queue (CityBite)

## 1) Write path — new order (API → DB → outbox / event)

1. **Client** sends `POST /orders` to **Ingress** → **Order API** (validates cart, restaurant hours, idempotency key if present).
2. **Transaction on primary:** insert `orders` (and line items), update inventory / slot where applicable, **append to outbox** table (or `NOTIFY` + outbox) for `OrderPlaced` — **one commit** to **one primary**.
3. **Response:** return **201** with `order_id` and status once the **commit** succeeds.
4. **Asynchronous (must not block response):** worker(s) or DB poll reads the **outbox** and enqueues to **message broker / queue** for `example2`-style work (push, email, analytics), or consumers pick **outbox in order**.

**Strong consistency (required for the customer and restaurant for this order):** the **order row** and payment/capture state as defined by product; **at-least-once** delivery to downstream if we use a queue, with **idempotent** consumers.

**Eventual (acceptable for growth):** **push/email** arrival within seconds; **warehousing/analytics** slices; **search** index and **recommendation** sidecars — **stale** by a bounded window is OK if documented.

## 2) Read path — kitchen “active orders” (partition key / index, `example1`)

- Queries **must** filter by **`restaurant_id`** (tenant scope), with a **composite index** e.g. `(restaurant_id, status, updated_at)` so the engine never **scans** the global open-order set. That is the same idea as **partitioning by `restaurant_id`** in `IndexedOrderBoard` in **`example1_scalability_hot_path_citybite.py`**: work grows with **this** restaurant’s rows, not **all** restaurants’ volume.
- Optional: **read replica** for the kitchen if primary is hot — **replication lag** (hundreds of ms) is often acceptable for “on the line” if UI polls or **short** inconsistency is tolerated; otherwise read from **primary** for the strictest view.

## 3) Cache — at least one (key, TTL/invalidation, stale behavior)

- **What:** **Redis (or groupcache)** for **read-mostly** menu and **item availability snapshot** for the **customer** browse flow, key e.g. `menu:{restaurant_id}:v` or per-restaurant **ETag** hash.
- **TTL / invalidation:** **TTL 60–120 s** at peak, plus **explicit invalidation** on menu publish from the restaurant backoffice. **SWR-style:** serve from cache, **revalidate in background** if desired.
- **On stale read:** user might see **outdated** price or 86’ed item for a short time; **mitigation** — re-check on **add-to-cart** and at **order submit** against **primary** (strong path). Product copy: “menu may take a minute to update.”

## 4) Where we do **not** block the HTTP response (`example2`)

- After commit, **do not** call SMS/push/email or heavy webhooks **inside** the `POST` handler. **Enqueue** the minimal event (order id, channel prefs) to a **queue**; **`example2_scalability_queue_workers_citybite.py`** models the **accept fast / drain in parallel** split.
- The **Order API** stays bounded in latency; **workers** scale on **queue depth** and **provider** throughput.

## ≥ Four concrete scalability risks addressed (this design)

1. **Hot primary** — outbox + async, **replica** for read-heavy kitchen/reporting.  
2. **O(n) kitchen queries** — **index / `restaurant_id` partition key** (`example1`).  
3. **Checkout + notify coupling** — **queue + workers** (`example2`).  
4. **Read amplification on menu** — **CDN + Redis** with **TTL** and **submit-time** validation.  
