# Part 2: Architecture under Growth
## Task 2.1: Data Plane — Reads, Writes, Caches

## 1. Overview
This section describes how CityBite handles the data path when traffic grows. The main goal is to keep the checkout flow fast while protecting the database and moving non-critical work out of the HTTP request.

---

## 2. Write Path for a New Order

### Write flow
1. Client sends `POST /orders` to the API.
2. API validates the request.
3. API writes the order to PostgreSQL inside a transaction.
4. API writes an outbox event in the same transaction, such as `OrderCreated`.
5. A background worker or relay publishes the outbox event to a queue or stream.
6. Downstream consumers process notifications, analytics, restaurant updates, and dispatch updates.

### Strongly consistent parts
These must stay strongly consistent:
- Order creation
- Payment confirmation
- Inventory or restaurant acceptance rules if they affect whether the order is valid
- Final database write for the order row

### Eventually consistent parts
These can be eventually consistent:
- Push notifications and emails
- Analytics dashboards
- Search indexing
- Restaurant reporting views
- Courier dispatch updates that do not change the original order record

### Why this split matters
The user should only wait for the critical transaction. Side effects such as notifications should not block checkout, because they can be retried later if the queue or worker is slow.

---

## 3. Read Path for Kitchen Active Orders

### Read flow
The kitchen dashboard for one restaurant should query only the orders relevant to that restaurant, not the entire system.

A good pattern is:
- Partition or index by `restaurant_id`
- Filter by active statuses such as `PLACED`, `COOKING`, `READY`
- Read only the rows needed for the current restaurant view

### Why this scales better
This follows the hot-path thinking from the lecture example: each restaurant query should touch only local data, not the global order set. If the system scans all orders for every dashboard refresh, the cost grows with total system size instead of local restaurant load.

### Example screen
This supports the restaurant tablet or kitchen screen that shows:
- New orders
- Orders being prepared
- Orders ready for pickup

---

## 4. Cache Proposal

### Cache 1: Restaurant menu and restaurant details
**Key**
- `restaurant:{id}:menu`
- `restaurant:{id}:profile`

**TTL / invalidation**
- TTL: 5 to 15 minutes for menu data
- Invalidate immediately when the restaurant updates menu items or availability

**Stale read behavior**
- If the cache is stale, the screen may briefly show an old menu item or price.
- For customer-facing browsing, this is acceptable if checkout still revalidates the final price on the server.
- If the cache misses, the API reloads the data from the database or object storage.

### Real CityBite screen
This cache helps the customer app home screen and restaurant menu page load faster during peak traffic.

### Cache 2: Active orders for restaurant dashboard
**Key**
- `active-orders:{restaurant_id}`

**TTL / invalidation**
- Short TTL such as 5–30 seconds, or event-driven invalidation when a new order or status change arrives

**Stale read behavior**
- A short delay is acceptable for dashboard refreshes.
- If the cache is stale, the kitchen screen may lag slightly, but the next refresh or event will correct it.

---

## 5. Queue or Stream: Where Not to Block HTTP

The HTTP response should not wait for:
- Notifications
- Analytics events
- Search indexing
- Non-critical dashboard fan-out

### Better approach
After the order is safely stored in the database and the outbox record is written, the API should return success. A queue or stream then carries the side effects to workers.

This is the same idea as decoupling checkout from outbound I/O: the HTTP request stays fast, and workers drain the backlog later.

---

## 6. Summary
CityBite should keep the order write path small and strongly consistent only where needed. Reads for the kitchen dashboard should use partition-aware access or indexes by `restaurant_id`. Caches should protect menu browsing and active-order dashboards, while queues should absorb notifications and other non-blocking work.
