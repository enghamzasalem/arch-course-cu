# Part 2.3: Saga Sketch — “Place Paid Order” (CityBite)

**Journey:** Customer places a paid order (catalog reserved, payment captured, order confirmed, dispatch notified).

**Choice:** **Orchestration** (central **Checkout Orchestrator** service or module) with compensations.  
*(Choreography is viable later; orchestration is clearer for money + inventory edge cases during extraction.)*

---

## Local steps per context (with compensating actions)

| Step | Context | Local action | If later step fails — compensation |
|------|---------|--------------|-------------------------------------|
| 1 | Catalog | Validate menu + price snapshot; **reserve** stock / kitchen capacity token | Release reservation token |
| 2 | Billing | Create **payment intent** / authorize funds | Void/cancel authorization |
| 3 | Ordering | Persist `Order` as `PLACED` (idempotent on client token) | Mark order `CANCELLED` + emit `OrderCancelled` |
| 4 | Billing | **Capture** payment | Issue refund (or partial refund policy) |
| 5 | Dispatch | Create delivery job / enqueue assignment | Cancel delivery job + notify dispatch |
| 6 | Notifications | Send “order confirmed” (async OK) | Send “order failed” correction (best effort) |

**No distributed two-phase commit fantasy:** each step is a **local transaction**; the orchestrator records saga state (`SAGA_ID`, step, last error) and drives forward or backward.

---

## Orchestration — two pros, one con

**Pros**

1. **Explicit failure handling:** retries, timeouts, and compensations live in one place—easier for payments and partial failures.
2. **Easier operations and tracing:** one correlation id across steps simplifies support during dinner rush incidents.

**Con**

- **Orchestrator becomes a coupling hub** if it grows huge—mitigate with modular orchestration + strict context APIs.

---

## Choreography alternative (brief)

Event-driven: `OrderPlaced` → Billing listens → `PaymentCaptured` → Dispatch listens…  
**Pros:** loose coupling, independent scaling. **Con:** harder to reason about global ordering and refunds across many listeners without strong observability.
