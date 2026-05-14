# Part 2.3 — Saga Sketch

## Selected Journey

Place Paid Order

---

## Local Steps by Context

### Step 1 — Order Context

The Order service creates a pending order.

Compensating action:
- Cancel the order if payment fails.

---

### Step 2 — Payment Context

The Payment service charges the customer.

Compensating action:
- Refund the payment if restaurant confirmation fails.

---

### Step 3 — Restaurant Context

The Restaurant service accepts the order.

Compensating action:
- Reject the order and trigger a refund.

---

### Step 4 — Notification Context

The Notification service sends confirmation messages to the customer.

Compensating action:
- Retry notification delivery asynchronously.

---

## Saga Style Choice

CityBite uses orchestration for this workflow.

### Advantages

1. Centralized coordination simplifies monitoring and debugging.
2. Easier rollback and failure handling.

---

### Disadvantage

The orchestrator becomes an additional operational dependency and may introduce extra complexity.