# Part 3.3 — Event Sourcing (Bonus) — CityBite

## 1. Overview

Event sourcing is a pattern where instead of storing only the current state of a system, CityBite stores a sequence of **immutable events** that describe everything that happened to an order over time.

This can improve auditability, debugging, and recovery after system failures.

---

## 2. Bounded Context: Order Lifecycle

We focus on a single bounded context:

> Order processing from creation → payment → preparation → delivery

Instead of updating a single "order" row repeatedly, CityBite stores events.

---

## 3. Event Log Structure

Each change in order state is appended as an event:

### Example Events

- `OrderCreated`
- `PaymentInitiated`
- `PaymentConfirmed`
- `PaymentFailed`
- `OrderAcceptedByRestaurant`
- `OrderPrepared`
- `OrderPickedUp`
- `OrderDelivered`

Each event includes:
- `order_id`
- timestamp
- payload (status, metadata, restaurant_id, etc.)

---

## 4. How System State is Reconstructed

Instead of reading a single row:

1. Fetch all events for an `order_id`
2. Replay them in order
3. Reconstruct current order state

Example:

```text
OrderCreated
→ PaymentConfirmed
→ OrderAcceptedByRestaurant
→ OrderPrepared
→ OrderPickedUp
```
# 5. Why Event Sourcing Helps

## 5.1 Debugging

If something goes wrong:

- You can replay events  
- You can see exactly where failure occurred  
- No hidden state corruption  

---

## 5.2 Recovery After Bugs

If a bug corrupts current state:

- Fix logic  
- Replay event log  
- Rebuild correct system state  

---

## 5.3 Auditability

Every action is recorded:

- Useful for financial tracking  
- Useful for dispute resolution  
- Useful for restaurant accountability  

---

# 6. Trade-offs

## Pros

- Full history of system behavior  
- Strong audit trail  
- Easier debugging of complex flows  

## Cons

- More storage usage  
- More complex query logic  
- Requires rebuilding state for reads  
- Harder to implement correctly  

---

# 7. When CityBite Would Use It

Event sourcing would be useful in CityBite for:

- Order state tracking (high-value workflow)  
- Payment history auditing  
- Delivery dispute resolution  

It is NOT ideal for:

- Simple read-heavy dashboards  
- Frequently changing non-critical data  

