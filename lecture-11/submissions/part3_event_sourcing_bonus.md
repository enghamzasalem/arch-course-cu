# Part 3.3 (Bonus) — Event Sourcing Sketch

## Bounded Context: Order Lifecycle

The order lifecycle is the ideal candidate for an event-sourced model in CityBite. An order transitions through a well-defined sequence of states, each triggered by a discrete business event. Storing these events as an append-only log — rather than overwriting a single `status` column — gives CityBite a complete, auditable history of every order.

---

## Events List

| # | Event Name | Payload (key fields) | Triggered By |
|---|------------|----------------------|--------------|
| 1 | `OrderPlaced` | `order_id`, `customer_id`, `restaurant_id`, `items[]`, `total_amount`, `timestamp` | Customer submits checkout |
| 2 | `PaymentInitiated` | `order_id`, `payment_provider`, `idempotency_key`, `timestamp` | Order API calls payment gateway |
| 3 | `PaymentSucceeded` | `order_id`, `transaction_id`, `amount_charged`, `timestamp` | Gateway returns success |
| 4 | `PaymentFailed` | `order_id`, `error_code`, `retry_count`, `timestamp` | Gateway returns error / circuit breaker open |
| 5 | `OrderConfirmed` | `order_id`, `estimated_prep_minutes`, `timestamp` | After `PaymentSucceeded` |
| 6 | `OrderReadyForPickup` | `order_id`, `restaurant_id`, `timestamp` | Restaurant marks order ready |
| 7 | `CourierAssigned` | `order_id`, `courier_id`, `eta_minutes`, `timestamp` | Dispatch worker assigns courier |
| 8 | `OrderDelivered` | `order_id`, `courier_id`, `delivered_at` | Courier confirms delivery |
| 9 | `OrderCancelled` | `order_id`, `reason`, `refund_amount`, `timestamp` | Customer, restaurant, or system |

The current state of any order is derived by replaying its events in sequence — there is no mutable `orders` row to update.

---

## How Replay Helps After a Bug

Suppose a bug is deployed that incorrectly calculates the `amount_charged` in `PaymentSucceeded` events — it applies a discount twice, undercharging customers. The bug is live for two hours before it is caught.

With a traditional mutable database, the `amount_charged` column has already been overwritten with the wrong value. Identifying affected orders requires cross-referencing application logs with the DB, and correcting the ledger means writing compensating UPDATE statements — error-prone and hard to audit.

With event sourcing:

1. The raw `PaymentSucceeded` events are immutable in the log — they record exactly what the gateway charged, not what the buggy code computed.
2. A corrected projection (read model) is deployed that recalculates `amount_charged` correctly from the gateway's `transaction_id`.
3. The projection is **replayed** from the beginning of the two-hour window, rebuilding the correct read model without touching the event log.
4. A reconciliation report is generated automatically by comparing the old projection's values against the replayed values — identifying every affected order in minutes.

This is the core recovery benefit of event sourcing: **the log is the truth; projections are disposable**. Any bug in a projection can be fixed and the projection rebuilt from the immutable event history, without data loss or manual SQL surgery.
