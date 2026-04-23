# Part 2 — Data Scaling (CityBite)

## 1. Overview

This section explains how CityBite handles data as the system grows, especially under peak load. The focus is on how data flows through the system—both for writes and reads—and how techniques like caching and queues help maintain low latency and high throughput.

---

## 2. Write Path — New Order

### 2.1 Flow

When a customer places an order, the flow looks like this:

1. Client sends order request → API  
2. API validates the request  
3. API writes the order to **PostgreSQL (primary database)**  
4. API publishes an event to a **queue (e.g. SQS / Kafka)**  
5. API responds to the client immediately  
6. Background workers process the event (notifications, analytics, etc.)  

---

### 2.2 Consistency Model

Not all parts of the system need the same level of consistency. CityBite separates what must be immediate from what can happen later.

#### Strong Consistency (Required)
- Order creation in the database  
- Payment confirmation  
- Inventory updates  

👉 These must complete successfully before responding to the user.

---

#### Eventual Consistency (Acceptable)
- Push notifications (SMS/email)  
- Analytics processing  
- Recommendation updates  

👉 These are handled asynchronously and can tolerate small delays.

---

## 3. Read Path — Kitchen Active Orders

### 3.1 Problem (from lecture example)

A naive implementation would scan all orders:

- Full table scan → **O(n)** complexity  

👉 This becomes inefficient as the total number of orders grows.

---

### 3.2 Scalable Approach

Instead, CityBite limits the scope of each query:

- Use an **index on `restaurant_id`**  
- Query only relevant rows for that restaurant  

Example:

```sql
SELECT * FROM orders 
WHERE restaurant_id = ? 
AND status != 'PICKED_UP';
```

---

## 3.3 Key Insight

Query cost should scale with the number of orders for a single restaurant **(O(k))**, not with the total system size **(O(n))**.

---

## 4. Caching Strategy

### 4.1 Use Case

The restaurant dashboard frequently refreshes active orders, which leads to repeated queries for the same data within short time intervals.

---

### 4.2 Cache Design

- **Cache key:** `active_orders:<restaurant_id>`  
- **Storage:** Redis (in-memory cache)  
- **TTL:** 5–10 seconds (short-lived to keep data reasonably fresh)  

---

### 4.3 Cache Behavior

**On request:**
- Check the cache first  
- If there is a cache miss → query the database  
- Store the result in the cache  

**On update:**
- Invalidate or refresh the cache to prevent stale data  

---

### 4.4 Trade-off

- Data may be slightly stale (a few seconds delay)  
- In return, database load is significantly reduced  

---

## 5. Queue and Decoupling (Lecture Example 2)

### 5.1 Problem

If the API performs external operations (such as sending notifications) during the request:

- Response time increases  
- Throughput drops under load  

---

### 5.2 Solution

CityBite uses a queue-based architecture:

- The API publishes events to a queue  
- Worker services process these events asynchronously  

---

### 5.3 Where NOT to Block HTTP

The API should **not wait** for:

- SMS delivery  
- Email sending  
- Push notifications  

These operations are handled outside the request-response cycle.

---

### 5.4 Benefits

- Faster checkout experience for users  
- Higher overall system throughput  
- Workers can scale independently  
- Improved failure handling (e.g., retries via queue)