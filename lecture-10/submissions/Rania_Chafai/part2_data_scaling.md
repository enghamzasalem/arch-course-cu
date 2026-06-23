# Part 2 — Data Plane: Reads, Writes, and Caching

## 2.1 Write Path — New Order

When a customer places a new order, the request follows this path:

1. **Client → Ingress → Order API**
2. API validates the request and processes business logic
3. Order is written to **PostgreSQL (primary database)**
4. A message is sent to a **queue** (e.g. SQS / Redis queue) for background processing
5. API returns a response to the user

### Consistency Model

* **Strong Consistency (Required):**

  * Order creation
  * Payment confirmation
  * Order status updates

* **Eventual Consistency (Acceptable):**

  * Notifications (push/email)
  * Analytics and reporting
  * Dashboard updates with slight delay

=> This ensures correctness for critical operations while allowing scalability for non-critical ones.

---

## 2.2 Read Path — Kitchen Active Orders

Restaurants need fast access to active orders in real time.

### Optimized Query Strategy

Instead of scanning all orders globally, the system uses:

* **Partition key / index:** `restaurant_id`
* Queries scoped to a single restaurant

### Example

```sql
SELECT * FROM orders
WHERE restaurant_id = ?
AND status = 'active';
```

### Benefits

* Reduces query cost from global dataset → per restaurant
* Improves latency for dashboard queries
* Scales with number of restaurants (multi-tenant isolation)

=> This follows the **hot path optimization** principle from Lecture 10.

---

## 2.3 Caching Strategy

### Cache: Menu Data

* **What is cached:** restaurant menus
* **Key:** `menu:<restaurant_id>`
* **TTL:** 5–10 minutes

### Why caching?

* Menu data changes infrequently
* High read frequency from customers
* Reduces repeated database queries

### Behavior on Cache Miss

1. Request goes to database
2. Result is stored in cache
3. Future requests served from cache

### Trade-off

* Slightly stale data is acceptable
* Improves performance significantly

---

## 2.4 Queue-Based Processing (Async)

Certain operations should not block the HTTP request.

### Example: Notifications

Instead of:

Sending notifications inside the API request (slow)

We use:

**Queue + Worker pattern**

Flow:

1. API places message in queue
2. Worker processes message asynchronously
3. Sends push/email notification

### Benefits

* Reduces API latency
* Improves user experience
* Allows parallel processing (scales with workers)

=> This follows the **example2 worker model** from Lecture 10.

---

## 2.5 Summary

CityBite improves scalability by:

* Keeping critical writes strongly consistent
* Optimizing read queries using partitioning
* Using caching to reduce database load
* Decoupling heavy operations using queues

This combination ensures that the system remains responsive and scalable under peak demand.
