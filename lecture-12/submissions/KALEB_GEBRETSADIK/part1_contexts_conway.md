# Part 1.1: Bounded Context Map & Conway's Law

## Bounded Contexts

| Context | Ubiquitous Language (≥4 terms) | Primary User | Owns |
|---|---|---|---|
| **Ordering** | Order, Line Item, Checkout, Placement, Cancellation | Customer | Order lifecycle, cart state, order history |
| **Payment** | Charge, Refund, Authorization, Settlement, Transaction | Finance/Customer | Payment records, charge attempts, refund state |
| **Dispatch** | Assignment, Driver, Route, ETA, Pickup, Delivery | Dispatcher/Driver | Driver location, delivery job, routing state |
| **Restaurant** | Menu, Item, Availability, Preparation, Ready Signal | Restaurant Staff | Menu catalog, item inventory, readiness status |
| **Notifications** | Alert, Channel, Preference, Delivery Receipt | All users | Notification log, user channel preferences |

## Integration Styles Between Adjacent Contexts

| Context Pair | Style | Reason |
|---|---|---|
| Ordering → Payment | **Sync REST API** (request/response) | Payment authorization is a blocker for order confirmation; the customer must know immediately if payment failed. |
| Ordering → Dispatch | **Async Event** (`OrderPaid` event) | Dispatch can start after payment is confirmed; no need to block the checkout response. |
| Ordering → Notifications | **Async Event** (`OrderPlaced`, `OrderCancelled`) | Fire-and-forget; notification latency doesn't affect core flow. |
| Restaurant → Dispatch | **Async Event** (`OrderReady`) | Dispatch only needs to know when food is ready; polling would waste resources. |
| Dispatch → Notifications | **Async Event** (`ETAUpdated`, `DriverAssigned`) | Status updates are non-blocking and high-frequency — a queue is the natural fit. |
| Payment → Notifications | **Async Event** (`PaymentFailed`, `RefundIssued`) | Outcome emails/pushes are not time-critical and must not slow down the payment flow. |

## Conway's Law Prediction

If CityBite keeps **one team** responsible for all five contexts, Conway's Law predicts the architecture will mirror the team's communication structure: a **single, deeply integrated module or schema** where ordering, payment, dispatch, restaurant, and notification logic all share the same database tables and call each other via in-process function calls. There will be no enforced boundaries. Over time, any attempt to split the system will be blocked by hidden coupling — shared ORM models, cross-context SQL joins, and implicit knowledge spread across the team. The architecture will become a **big ball of mud**, not because of bad intent but because a single team optimises for local convenience, not inter-team contracts.
