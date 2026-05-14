# Part 3 — Task 3.3 (Bonus): Event Sourcing Sketch
**Assignment:** Software Architecture — Lecture 11 (Availability and Services)
**Bounded context:** Order lifecycle

---

## Bounded Context: Order Lifecycle

The Order bounded context owns every state transition from cart submission to delivery confirmation. It is the right candidate for an event log because (a) order state is the single most audited entity in CityBite — finance, support, and dispatch all query it independently — and (b) the `PAYMENT_PENDING` fallback introduced in Part 2 creates a recovery scenario where knowing the exact sequence of events is essential to avoiding double-charges.

---

## Event List

Each event is immutable, append-only, and carries a monotonic sequence number, a wall-clock timestamp, and a correlation ID linking it to the originating HTTP request.

| # | Event name | Emitted by | Key payload fields |
|---|---|---|---|
| 1 | `OrderSubmitted` | Order API | `order_id`, `customer_id`, `cart_items[]`, `total_amount` |
| 2 | `PaymentAuthorized` | Order API (gateway callback) | `payment_ref`, `amount_authorized`, `gateway` |
| 3 | `PaymentFailed` | Order API (gateway error / CB open) | `reason`, `gateway_error_code` |
| 4 | `OrderQueuedPendingPayment` | Order API (fallback path) | `retry_after_seconds` |
| 5 | `PaymentRetrySucceeded` | Background retry worker | `payment_ref`, `attempt_number` |
| 6 | `OrderConfirmed` | Order API | `confirmed_at` |
| 7 | `DriverAssigned` | Dispatch Worker | `driver_id`, `eta_seconds` |
| 8 | `OrderPickedUp` | Dispatch Worker | `pickup_at` |
| 9 | `OrderDelivered` | Dispatch Worker | `delivered_at`, `actual_duration_seconds` |
| 10 | `OrderCancelled` | Order API or Customer | `cancelled_by`, `reason`, `refund_due` |

The **current state** of any order is the left-fold of this event stream: `state = events.reduce(apply, initial)`. Postgres stores the raw event rows; a materialised read model (the Lecture 10 projection) caches the derived `status` column for fast lookups.

---

## How Replay Helps After a Bug

**Scenario:** A deploy introduces a bug in the payment retry worker that incorrectly emits `OrderConfirmed` without a preceding `PaymentAuthorized` or `PaymentRetrySucceeded` event — confirming orders for which payment was never captured. The bug runs for 40 minutes before detection. Forty orders are affected.

**Without event sourcing:** The Postgres `orders` table shows `status = CONFIRMED` for all forty rows. There is no record of whether payment was actually collected. Finance must manually cross-reference gateway logs (held by a third party, rate-limited to export) against order rows to determine which orders have a payment reference and which do not. The reconciliation takes hours; some orders may already be dispatched.

**With event sourcing:**

1. The event log for each affected order is fetched in sequence. Any order where `OrderConfirmed` appears without a preceding `PaymentAuthorized` or `PaymentRetrySucceeded` is immediately identifiable — the missing event is itself the evidence.

2. The buggy `OrderConfirmed` events are marked with a compensating event `OrderConfirmationReverted` (events are never deleted; the log is append-only). The materialised read model is rebuilt by replaying the corrected stream: affected orders revert to `PAYMENT_PENDING`.

3. The retry worker re-processes the queue. Orders where payment can now be captured receive `PaymentRetrySucceeded` → `OrderConfirmed` in the correct sequence. Orders where the customer's card is declined receive `PaymentFailed` → `OrderCancelled` with `refund_due = false` (nothing was charged).

4. The complete audit trail — original submission, the erroneous confirmation, the reversion, and the final resolution — is permanently preserved in the event log. Regulators or the customer support team can read the exact timeline of any individual order with a single query.

**The key property:** because the event log is the source of truth and the relational state is a derived projection, fixing the projection is a matter of replaying events through the corrected `apply` function — no data surgery on live rows, no risk of leaving the database in a partially-corrected state, and no dependence on external audit logs that may be incomplete or rate-limited.

---

*This sketch is intentionally bounded to the Order context. Payment, Driver, and Restaurant contexts would each have their own event streams and would communicate via domain events published to the Dispatch Queue — not by reading each other's event logs directly.*
