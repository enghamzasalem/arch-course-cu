# Task 2.3: Saga sketch

## Chosen Journey: "Place Paid Order"

This journey spans three bounded contexts — Ordering, Payment, and Dispatch — and involves a payment charge that must be rolled back if a later step fails. It is the canonical use case for a saga because a distributed two-phase commit (2PC) across three independent databases would be fragile, slow, and operationally nightmarish.

---

## Local Steps and Compensating Actions

| Step | Context | Local Action | Compensating Action (if a later step fails) |
|------|---------|--------------|---------------------------------------------|
| 1 | **Ordering** | Create order record with `status: PENDING`; publish `OrderInitiated` event | Set `status: CANCELLED`; publish `OrderCancelled` event |
| 2 | **Payment** | Authorise and capture payment; record `PaymentSucceeded` or `PaymentFailed` event | Issue refund (`Refund` record); publish `PaymentRefunded` event |
| 3 | **Ordering** | On `PaymentSucceeded`: set `status: CONFIRMED`; publish `OrderConfirmed` event | (Compensation already handled by Payment refund in step 2) |
| 4 | **Dispatch** | On `OrderConfirmed`: create `Delivery` record; assign courier; publish `CourierAssigned` | Release courier back to available pool; publish `DeliveryAborted` |
| 5 | **Ordering** | On `CourierAssigned`: set `status: IN_DELIVERY` | Set `status: CANCELLED`; trigger Payment compensation if needed |

### Failure Scenarios

**Payment fails at step 2:**
- Payment context publishes `PaymentFailed`.
- Ordering saga handler receives it → runs compensation for step 1 (sets order to `CANCELLED`).
- No Dispatch involvement needed — the saga never reached step 4.

**Courier assignment fails at step 4** (e.g. no couriers available in zone):
- Dispatch publishes `CourierAssignmentFailed`.
- Ordering saga handler receives it → sets order to `CANCELLED`; triggers Payment compensation (refund).
- Payment context processes the refund and publishes `PaymentRefunded`.
- Notification context sends "We're sorry, your order was cancelled" message to the customer.

---

## Choreography vs Orchestration

### Choice: **Choreography**

In this design, each context reacts to events published by other contexts. There is no central coordinator. The flow is:

```
Ordering publishes OrderInitiated
  → Payment subscribes, processes, publishes PaymentSucceeded / PaymentFailed
    → Ordering subscribes to PaymentSucceeded, publishes OrderConfirmed
      → Dispatch subscribes to OrderConfirmed, publishes CourierAssigned
        → Ordering subscribes to CourierAssigned, updates status
```

### Two Pros of Choreography

1. **No single point of failure.** There is no central orchestrator service that, if it goes down, freezes all in-flight sagas. Each context is independently deployable and handles its own slice of the saga. This aligns well with the availability patterns from Lecture 11 — the system degrades gracefully rather than failing completely.
2. **Loose coupling between contexts.** The Payment context does not know that Dispatch exists. It only knows it must publish `PaymentSucceeded` or `PaymentFailed`. Adding a new context that reacts to payment events requires zero changes to the Payment service — it simply subscribes to the existing event.

### One Con of Choreography

1. **Hard to trace and debug.** Because there is no central record of a saga's state, diagnosing a stuck or partially-completed order requires correlating events across multiple services' logs using a shared `order_id` correlation key. Without good distributed tracing, it is difficult to answer "why is order `ord_abc123` stuck at step 3?" This is the main operational cost of choreography over orchestration.
