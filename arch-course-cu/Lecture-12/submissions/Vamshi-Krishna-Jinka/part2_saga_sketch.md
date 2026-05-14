# Part 2: Data, APIs, Sagas
## Task 2.3: Saga Sketch

## 1. Journey Chosen
### Place Paid Order

This saga covers the cross-context flow for a customer placing a paid order in CityBite. The goal is to complete the order without using a distributed two-phase commit, which would be too fragile and too expensive for this system.

---

## 2. Saga Flow by Context

### Step 1: Ordering Context
- Create the order in `PENDING` state.
- Reserve cart items and create an order record.
- Publish `OrderPlaced`.

**Compensating action if later failure occurs:**
- Mark the order as `CANCELLED`
- Release reserved items

---

### Step 2: Payments Context
- Receive `OrderPlaced`.
- Authorize payment.
- If authorization succeeds, publish `PaymentAuthorized`.
- If authorization fails, publish `PaymentFailed`.

**Compensating action if a later step fails:**
- Void the authorization if needed
- Refund if capture already happened

---

### Step 3: Restaurant Operations Context
- Receive `PaymentAuthorized`.
- Accept the order for preparation.
- Publish `RestaurantAccepted`.

**Compensating action if a later step fails:**
- Mark the order as rejected
- Release the customer-facing promise that the order is confirmed

---

### Step 4: Dispatch Context
- Receive `RestaurantAccepted`.
- Assign a courier when the order is near ready.
- Publish `CourierAssigned`.

**Compensating action if a later step fails:**
- Unassign courier
- Requeue delivery assignment

---

### Step 5: Notifications Context
- Receive each major event and send customer updates.
- Notify the customer when the order is confirmed, accepted, and out for delivery.

**Compensating action if a later step fails:**
- Retry delivery
- Store the notification for later resend

---

## 3. Orchestration vs Choreography

### Choice: Choreography
For this saga, choreography is the better choice because each context already owns its own local work and reacts to domain events.

### Two pros
1. **Loose coupling**: Ordering, Payments, Restaurant Operations, Dispatch, and Notifications can evolve independently as long as they keep publishing and subscribing to the agreed events.
2. **Good fit for microservices**: Each service owns its own local transaction and publishes the next step only when its work succeeds.

### One con
- **Harder to trace**: The full business journey is spread across events, so debugging and observing the saga is more difficult than with a central orchestrator.

---

## 4. Why not two-phase commit
A distributed two-phase commit would make the system slower, more fragile, and more tightly coupled. CityBite does not need perfect atomicity across all contexts; it needs a practical flow with compensations when later steps fail. A saga gives that balance.

---

## 5. Summary
The paid-order journey can be implemented as a saga where each context does local work and publishes an event for the next step. If something fails later, compensating actions undo the earlier business effects. Choreography is the better fit because it keeps the services independent and avoids a distributed monolith style of coordination.
