# Part 2.3: Saga Sketch

## Journey: Place Paid Order

This spans three contexts: **Ordering**, **Payment**, and **Dispatch**.

---

## Local Steps & Compensating Actions

| Step | Context | Local Action | Compensating Action (if later step fails) |
|---|---|---|---|
| 1 | Ordering | Create order record with status `PENDING` | Delete/mark order `CANCELLED` |
| 2 | Payment | Authorize and charge payment method | Issue full refund (`/refunds`) |
| 3 | Dispatch | Create delivery job and assign a driver | Cancel delivery job, notify driver |
| 4 | Ordering | Mark order status `CONFIRMED`, emit `OrderConfirmed` event | — (terminal success) |

**Example failure:** If step 3 (Dispatch) fails (no drivers available), the saga runs compensations in reverse — Payment issues a refund (step 2 compensation), and Ordering marks the order `CANCELLED` (step 1 compensation). The customer receives a notification via the async `OrderCancelled` event.

---

## Choreography vs Orchestration

**Choice: Choreography**

Each service reacts to domain events:
- Ordering emits `OrderCreated` → Payment listens and charges
- Payment emits `ChargeCaptured` → Dispatch listens and assigns a driver
- Dispatch emits `DriverAssigned` → Ordering listens and confirms the order

**Two Pros:**
1. **Loose coupling:** No central orchestrator knows about all services. Services can be deployed and scaled independently.
2. **Resilience:** No single point of failure. If the orchestrator crashes in an orchestration model, all in-flight sagas stall.

**One Con:**
1. **Hard to trace:** The overall saga flow is implicit — spread across multiple event handlers. Debugging a partial failure requires correlating events across service logs using a shared `correlation_id`. This makes observability more expensive.
