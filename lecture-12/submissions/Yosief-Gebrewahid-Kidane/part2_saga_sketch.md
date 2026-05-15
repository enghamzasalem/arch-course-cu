# Part 2 — Saga Sketch (CityBite)

## 1. Overview

CityBite’s “place paid order” workflow involves multiple bounded contexts:
- Ordering
- Payments
- Restaurant Operations
- Notifications
- Dispatch

Because these systems are distributed, CityBite cannot rely on a traditional two-phase commit across all services. Instead, the platform uses a **saga pattern** where each service performs a local transaction and publishes events for the next step.

If a later step fails, compensating actions are triggered to keep the system consistent.

---

# 2. Selected Journey — Place Paid Order

## Goal

A customer places and pays for a food order successfully.

---

# 3. Saga Steps by Context

## Step 1 — Ordering Context

### Action
- Create order with status `PENDING_PAYMENT`

### Local Transaction
- Store order in Ordering database

### Event Published
```text
OrderCreated
```

---

## Step 2 — Payments Context

### Action
- Authorize customer payment through payment gateway

### Local Transaction
- Store transaction record

### Success Event
```text
PaymentAuthorized
```

### Failure Event
```text
PaymentFailed
```

---

## Compensation if Payment Fails

### Ordering Context Compensation
- Mark order as `CANCELLED`

### Notifications Context Compensation
- Notify customer that payment failed

This avoids leaving incomplete unpaid orders in the system.

---

# 4. Step 3 — Restaurant Operations Context

### Action
- Add order to restaurant kitchen queue

### Local Transaction
- Store active kitchen order

### Event Published
```text
OrderAcceptedByRestaurant
```

---

## Compensation if Restaurant Rejects Order

If the restaurant cannot fulfill the order:
- Payment service triggers refund
- Ordering context updates order to `REJECTED`
- Notification service informs customer

---

# 5. Step 4 — Dispatch Context

### Action
- Assign courier
- Estimate delivery ETA

### Event Published
```text
CourierAssigned
```

---

## Compensation if No Courier Is Available

Possible fallback:
- Delay dispatch
- Retry courier assignment
- Cancel order after timeout and trigger refund

---

# 6. Step 5 — Notifications Context

### Action
Send:
- Push notification
- SMS
- Email confirmation

### Notes
This step is eventually consistent and fully asynchronous.

The customer may receive notifications slightly later even though the order is already accepted.

---

# 7. Choreography vs Orchestration

## Chosen Approach: Choreography

CityBite uses event-driven choreography where each service reacts to events independently.

---

## Advantages

### 1. Loose Coupling

Services communicate through events instead of direct centralized coordination. This allows teams to evolve services more independently.

---

### 2. Better Scalability

Each context can process events asynchronously and scale based on its own workload.

For example:
- Notification workers scale independently
- Dispatch systems scale independently from checkout traffic

---

## Disadvantage

### Harder Debugging and Visibility

Because there is no single central coordinator, tracing failures across multiple services becomes more complex.

To mitigate this, CityBite would need:
- Distributed tracing
- Correlation IDs
- Centralized logging

---

# 8. Why CityBite Avoids Two-Phase Commit

A distributed two-phase commit across:
- Payments
- Orders
- Restaurants
- Dispatch

would introduce:
- Tight coupling
- High latency
- Reduced availability
- Greater operational complexity

The saga approach accepts temporary inconsistency while improving flexibility and resilience.

