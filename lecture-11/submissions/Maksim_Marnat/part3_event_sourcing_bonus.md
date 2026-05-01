# Part 3.3 (bonus) — Event sourcing sketch: Order lifecycle

## Bounded context

**Order fulfillment** — everything from “cart frozen” through payment outcome to “accepted by kitchen” and terminal states (delivered / cancelled).

## Events (append-only facts)

| Event | Payload (informal) | Why it matters |
|-------|-------------------|----------------|
| `OrderDrafted` | cart_id, line items hash, customer id | Audit trail; replay rebuilds intent. |
| `PaymentRequested` | order_id, idempotency_key, amount | Correlates with PSP; dedup on replay. |
| `PaymentCaptured` / `PaymentFailed` | txn_ref, reason code | Financial truth; disputes. |
| `OrderAcceptedByRestaurant` | restaurant_id, SLA timestamp | Fulfillment clock starts. |
| `OrderReadyForPickup` / `OrderDelivered` | courier_id optional | Ops metrics and customer comms. |

## How replay helps after a bug

If a deploy **miscomputes transition** (e.g. marks `Delivered` without `PaymentCaptured`), we **stop traffic**, **fix code**, and **replay events from the append-only log** into a new projection—or **rebuild read models** from scratch from event `seq`. Because facts are immutable, we recover **consistent narrative** without silently patching rows; **audit** can prove what was announced to PSP and customer at each step.
