# Task 2.3 - Saga sketch

## Journey

"Place paid order" - the customer taps **Place Order** in the app. We must take payment, create the order, hand it to dispatch, and notify the customer. Each of these lives in a different bounded context, so we cannot wrap them in one ACID transaction. We use a saga: a sequence of local transactions, each with a compensating action if a later step fails.

## Local steps and compensations

| # | Context | Local step | Compensating action if a later step fails |
|-|-|-|-|
| 1 | Orders | create order row with status `PENDING` | mark order `CANCELLED`, emit `OrderCancelled` event |
| 2 | Payments | authorize charge against the customer's payment method (called synchronously by Orders at checkout) | void the authorization, or refund if it was already captured |
| 3 | Orders | move order status `PENDING` -> `PLACED`, emit `OrderPlaced` event | mark order `CANCELLED`, emit `OrderCancelled` event |
| 4 | Dispatch | accept the order, assign a courier, compute ETA | release the courier assignment, emit `DispatchReleased` event |
| 5 | Notifications | on `OrderPlaced` send "order confirmed" message to customer | no true compensation; if `OrderCancelled` arrives later, send a follow-up cancellation message |

The important point: each step only changes its own database. There is no two-phase commit across services. If a later step fails, we do not "undo" earlier steps with a magic rollback - we run their compensating actions, which are normal business operations (cancel, refund, release).

A small but real example: if Dispatch cannot find a courier in the area, it emits `DispatchFailed`. Orders listens, marks the order `CANCELLED`, and emits `OrderCancelled`. Payments listens for `OrderCancelled` and runs its compensation (void the authorization, or refund if already captured). Notifications listens for `OrderCancelled` and sends the cancellation message to the customer. Each context only reacts to events that belong to the order / payment lifecycle, not to events from another team's internal domain.

## Choreography or orchestration

**Choice: choreography.**

The Orders -> Payments authorization at step 2 stays a synchronous API call (we need an immediate yes / no at checkout, matching the integration style chosen earlier). Everything after `OrderPlaced` - Dispatch picking up the order, Notifications sending the message, the whole failure / compensation chain - runs through events. There is no central brain telling each context what to do next; each service reacts to the events it cares about.

**Pro 1 - low coupling between contexts.** No service has to know the full flow. Adding a new context later (for example a loyalty service that wants to award points on `OrderPlaced`) means subscribing to events, with zero changes in Orders, Payments, or Dispatch.

**Pro 2 - matches the team setup.** Each team owns its events and its compensations. There is no shared orchestrator codebase that becomes a coordination point and slows everyone down.

**Con - the end-to-end flow is hard to see.** Because the logic is spread across services and event subscriptions, no single place answers "where is order o_123 stuck right now?". We need distributed tracing and a correlation id on every event to debug a stuck saga, and that observability work is a real cost.