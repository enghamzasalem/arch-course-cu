# Task 3.3 (Optional) - Event Sourcing Sketch

## Bounded context

Order lifecycle (place paid order, from creation to confirmed and paid).

Right now we store only the current order status in Postgres ("pending", "pending payment", "confirmed and paid"). With event sourcing we also write an append-only log of what happened to each order, and the current status becomes a projection (a fold) over that log.

## Events

For one order, we append events like:

- `OrderPlaced` (customer id, items, total)
- `PaymentAttempted` (gateway request id)
- `PaymentBlockedByBreaker` (breaker was open at this moment)
- `PaymentRetryQueued` (worker job created)
- `PaymentSucceeded` (gateway transaction id)
- `OrderConfirmed`
- `NotificationSent`

Each event has a timestamp and an order id. We never delete or update them, we only append. The current status is computed by replaying the events in order.

## How replay helps after a bug

Imagine a bug in the background worker during a payment gateway outage. The worker successfully retries the payment but forgets to update the order status to "confirmed and paid" for some orders. Customers were charged but their orders stay stuck in "pending payment" in the DB.

With only the current-status table this is hard to fix: we do not know which orders were actually paid versus which ones were never charged.

With event sourcing it is much easier:
- The `PaymentSucceeded` event is in the log even if the status update was skipped, because the worker writes the event before updating the projection.
- We replay the events for all stuck orders. The replay logic is correct, so the projection ends up in the right state ("confirmed and paid") for the orders that really did get paid.
- For audit, we can also answer questions like "which orders hit `PaymentBlockedByBreaker` during the outage on day X" by filtering the log.

This is a recovery and audit benefit. It does not replace the breaker or the retry logic, but it gives us a safety net when our own code has a bug, because the truth lives in the event log instead of in a possibly-wrong status column.