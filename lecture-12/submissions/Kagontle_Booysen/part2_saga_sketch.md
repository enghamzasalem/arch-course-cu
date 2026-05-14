# Part 2 — Task 2.3: Saga Sketch

---

## Journey: "Place Paid Order"

A customer submits a cart. The outcome must be: order record created, payment authorised, restaurant notified, and delivery job queued — or every step that succeeded is rolled back cleanly. No distributed two-phase commit; no shared lock across contexts. Each context commits only its own local transaction and publishes an event or calls a compensating action if a later step fails.

---

## Orchestration Choice

CityBite uses **orchestration** for this saga. An explicit `OrderSaga` orchestrator — a stateful component living inside the Ordering context — drives the sequence by issuing commands to other contexts and waiting for reply events. The orchestrator is the only participant that knows the full flow; each context knows only its local step.

### Two Pros

**1. Explicit, inspectable state machine.** The saga's current step, compensations outstanding, and failure reason are all held in a single `saga_instances` table inside the Ordering schema. When a saga stalls mid-flight — payment gateway timeout at 2 a.m. — an on-call engineer queries one table and sees the exact state. With choreography, reconstructing the current state of a failing saga requires correlating events across five separate event logs in five separate schemas, each with its own clock skew and retention policy.

**2. Simpler cyclic-dependency avoidance.** In choreography, Payment would need to listen to Ordering events and Ordering would need to listen to Payment events — a bidirectional dependency that is invisible in the code but present in the runtime topology. The orchestrator breaks this: Payment only ever receives commands from and replies to the orchestrator. No context needs to know that another context exists.

### One Con

**Orchestrator becomes a bottleneck and single point of failure for this flow.** Every "place paid order" journey must pass through the `OrderSaga` process. If the Ordering service is down, no new paid orders can be placed — even if Payment, Dispatch, and Catalogue are all healthy. With choreography, a Payment outage would block only the payment step, not the orchestrator. This risk is mitigated by the Kubernetes deployment (multiple replicas, Lecture 9 baseline) and the saga state table acting as a crash-recovery log: on restart, the orchestrator replays any in-progress saga from its last persisted step.

---

## Saga Steps and Compensating Actions

The saga is triggered by the customer pressing "Confirm Order." Each row is one local transaction. Compensating actions are listed for every step that can be undone; steps that are naturally idempotent or terminal are noted.

---

### Step 1 — Ordering: Create Order Record

**Context:** Ordering

**Local transaction:**
- Insert row into `orders` with status `PLACED`
- Insert rows into `order_lines` (with price/name snapshots from Catalogue, fetched synchronously before saga starts)
- Insert `OrderCreated` event into `outbox_events`
- Insert `saga_instances` row with `step = AWAITING_PAYMENT_AUTH`

**Orchestrator action after commit:**
- Send `AuthorisePayment` command to Payment context (sync HTTP call via `PaymentPort` adapter — the port/adapter pattern from `example1`)

**Compensating action if a later step fails:**
- `CancelOrder`: update `orders.status` to `CANCELLED`, insert `OrderCancelled` into `outbox_events`
- This is the compensation that runs if Payment authorisation or Dispatch assignment subsequently fails

---

### Step 2 — Payment: Authorise Payment

**Context:** Payment

**Local transaction:**
- Call payment gateway via `PaymentPort.authorize_payment(cents, customer_ref)` (adapter wraps Stripe or Adyen — no gateway name leaks into the domain table)
- Insert `payment_intents` row with status `AUTHORISED`
- Insert `authorisations` row with `gateway_auth_token`
- Insert `PaymentAuthorised` event into `outbox_events`

**Reply to orchestrator:**
- Sync HTTP 200 with `{ intentId, authorisedAmount }` on success
- Sync HTTP 402/503 on failure (gateway decline or timeout)

**Compensating action if a later step fails:**
- `VoidAuthorisation`: call gateway void endpoint, update `payment_intents.status` to `VOIDED`
- Insert `PaymentVoided` event into `outbox_events` (consumed by Notifications to tell the customer the charge was released)
- Note: if the gateway call in the compensation itself fails, the orchestrator retries with exponential back-off up to a threshold, then escalates to a manual ops queue — void is idempotent on the gateway side

---

### Step 3 — Ordering: Confirm Order Accepted

**Context:** Ordering (orchestrator resumes after Payment reply)

**Local transaction:**
- Update `orders.status` to `ACCEPTED`
- Update `saga_instances.step` to `AWAITING_DISPATCH_ASSIGNMENT`
- Insert `OrderAccepted` event into `outbox_events`

**Orchestrator action after commit:**
- Publish `OrderReadyForDispatch` event to the message broker (async — Dispatch is not called synchronously because job assignment is not time-critical for the customer's confirmation response)

**Compensating action:**
- If Dispatch subsequently fails to assign a courier, revert to `CANCELLED` (Step 1 compensation) and trigger Step 2 void — the customer is informed the restaurant is unavailable

---

### Step 4 — Dispatch: Assign Delivery Job

**Context:** Dispatch

**Local transaction:**
- Consume `OrderReadyForDispatch` event
- Insert `delivery_jobs` row with status `PENDING_COURIER`
- Run zone-matching logic to find available courier
- Update `delivery_jobs.status` to `ASSIGNED` (or `UNASSIGNABLE` if no courier found in zone)
- Insert `DeliveryJobAssigned` or `DeliveryJobUnassignable` event into Dispatch outbox

**Reply to orchestrator (async):**
- Orchestrator subscribes to `DeliveryJobAssigned` / `DeliveryJobUnassignable` correlated by `order_ref`

**Compensating action if job was assigned but order is later cancelled:**
- `CancelDeliveryJob`: update `delivery_jobs.status` to `CANCELLED`, notify courier via Notifications context
- If courier has already picked up the order (status `IN_TRANSIT`), compensation escalates to ops — the saga cannot mechanically undo a physical pickup

---

### Step 5 — Ordering: Finalise Saga

**Context:** Ordering (orchestrator receives `DeliveryJobAssigned`)

**Local transaction:**
- Update `orders.status` to `DISPATCHED`
- Update `saga_instances.step` to `COMPLETED`
- Insert `OrderDispatched` event into `outbox_events`

**No compensating action:** this is the terminal happy-path step. The saga is now in a fully committed state across all contexts.

---

### Step 6 — Notifications: Fan-Out (independent, not part of saga commit chain)

**Context:** Notifications

**Local transaction:**
- Consumes `OrderAccepted`, `OrderDispatched`, `PaymentAuthorised`, `PaymentVoided` events from the broker
- Renders templates and dispatches push/SMS/email via SaaS APIs
- Records `delivery_receipts`

**Note:** Notifications is deliberately outside the saga's compensation chain. A failed push notification does not roll back the payment or the order. If a notification fails, the Notifications context retries with its own back-off policy. The saga is not aware of notification outcomes — this is the fire-and-forget async relationship defined in Task 1.1.

---

## Failure Paths and Compensation Matrix

| Failing Step | Compensations Triggered (in reverse order) |
|---|---|
| Step 2: Payment declines | Step 1 compensation: CancelOrder. Saga ends. No courier job was created. |
| Step 2: Payment gateway timeout | Orchestrator retries Step 2 up to 3× with back-off. If all fail: Step 1 CancelOrder. |
| Step 3: Ordering DB crash after authorisation | Orchestrator replays from `saga_instances` on restart. Step 3 is idempotent (upsert on order_id). |
| Step 4: No courier in zone (Unassignable) | Step 3 inverse: OrderCancelled. Step 2 compensation: VoidAuthorisation. Step 1 compensation: CancelOrder. |
| Step 4: Dispatch service down | Orchestrator waits with timeout (e.g. 30 s). If timeout: same as Unassignable path. |
| Step 5: Ordering DB crash before finalise | Orchestrator replays; Step 5 is idempotent (upsert on saga_id). |

---

## Saga State Machine (Orchestrator View)

```
[START]
   │
   ▼
AWAITING_PAYMENT_AUTH  ──(decline / timeout)──► COMPENSATING_VOID ──► CANCELLED
   │
   │ PaymentAuthorised
   ▼
AWAITING_DISPATCH_ASSIGNMENT  ──(unassignable)──► COMPENSATING_VOID ──► CANCELLED
   │
   │ DeliveryJobAssigned
   ▼
COMPLETED
```

The `saga_instances` table persists the current state name. On orchestrator restart, any row not in `COMPLETED` or `CANCELLED` is replayed from its last persisted step. This makes the saga **durable across crashes** without a distributed lock — the Ordering schema's Postgres instance is the single source of truth for saga progress.

---

## Explicit Trade-off: Flexibility vs Consistency

**Flexibility gained:** Each context commits only its own local transaction. The Ordering DB, Payment DB, and Dispatch DB are never locked simultaneously. A slow payment gateway does not hold a lock on the orders table. Contexts can be deployed and upgraded independently during the saga's execution — the saga will resume from the `saga_instances` state on the next orchestrator restart.

**Consistency cost accepted:** The system is only **eventually consistent** across contexts. Between Step 2 (payment authorised) and Step 5 (order dispatched), there is a window where the payment is authorised but the order is not yet confirmed in Dispatch. If a customer queries their order status during this window, they see `ACCEPTED` — not `DISPATCHED`. This is acceptable for food delivery but would require more careful design in, e.g., a financial settlement context where partial commitment is regulatory-problematic.

**The alternative — distributed two-phase commit — is explicitly rejected** because it requires a transaction coordinator that holds locks across the Ordering, Payment, and Dispatch databases simultaneously. Under load (Lecture 10 scalability) this becomes a bottleneck; under failure (Lecture 11 availability) a coordinator crash leaves all participants in a blocked prepared state until the coordinator recovers.

---

*Vocabulary aligned with Lecture 12 (saga, orchestration vs choreography, compensating transaction, local transaction), example1_flexibility_coupling_citybite.py (PaymentPort / ports-and-adapters used in Step 2 gateway call), Lecture 9 (outbox pattern, Postgres baseline), Lecture 11 (circuit breaker, availability patterns referenced in retry logic).*
