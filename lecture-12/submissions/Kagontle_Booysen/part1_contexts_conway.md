# Part 1: Bounded Contexts & Conway's Law — CityBite

---

## Task 1.1 — Bounded Context Map

CityBite is divided into five business-aligned bounded contexts. Each context owns its domain language, its data, and its primary behaviour. No context reaches into another's database.

---

### Context 1 — Ordering

**Primary user:** Customer (and restaurant staff confirming items)

**Ubiquitous language:** `PlacedOrder`, `OrderLine`, `CartSession`, `OrderStatus` (PLACED → ACCEPTED → READY → DISPATCHED → DELIVERED), `CancellationReason`, `ItemAvailability`

**Owns:**
- Data: orders table, order-line items, order lifecycle state machine
- Behaviour: cart management, order submission, status transitions, cancellation rules

---

### Context 2 — Catalogue & Inventory

**Primary user:** Restaurant operator

**Ubiquitous language:** `Menu`, `MenuItem`, `PriceVariant`, `RestaurantProfile`, `OperatingHours`, `SoldOut`, `PublishedMenu`

**Owns:**
- Data: restaurant profiles, menu items, pricing, availability flags
- Behaviour: menu publishing, item availability toggling, operating-hour enforcement

---

### Context 3 — Payment

**Primary user:** Customer (implicitly), Finance team (reporting)

**Ubiquitous language:** `PaymentAuthorisation`, `Charge`, `Refund`, `PaymentMethod`, `SettlementBatch`, `ChargebackClaim`, `PaymentPort` (from `example1_flexibility_coupling_citybite.py`)

**Owns:**
- Data: payment intents, authorisation tokens, refund records, settlement ledger
- Behaviour: authorise, capture, void, refund; gateway adapter selection via `PaymentPort`

---

### Context 4 — Dispatch & Logistics

**Primary user:** Courier, Dispatch coordinator

**Ubiquitous language:** `DeliveryJob`, `Courier`, `Route`, `ETA`, `PickupConfirmation`, `ProofOfDelivery`, `ZonePolygon`

**Owns:**
- Data: delivery jobs, courier assignments, GPS checkpoints, zone definitions
- Behaviour: job assignment, route optimisation (via Maps SaaS), ETA calculation, courier tracking

---

### Context 5 — Notifications

**Primary user:** Customer, Restaurant operator, Courier (all as recipients)

**Ubiquitous language:** `NotificationEvent`, `Channel` (push, SMS, email), `Template`, `DeliveryReceipt`, `Preference`, `SuppressedAddress`

**Owns:**
- Data: notification templates, channel preferences, delivery receipts
- Behaviour: fan-out to SMS/push/email SaaS, template rendering, opt-out enforcement

---

## Integration Styles Between Adjacent Contexts

| Pair | Style | Rationale |
|---|---|---|
| Ordering → Payment | **Sync REST call** (request/reply) | Checkout must know immediately whether the charge is authorised before confirming the order to the customer. Failure needs a synchronous error path. |
| Ordering → Catalogue | **Sync REST call** (read-only query at checkout) | Price and availability must be validated at the moment of order submission to prevent accepting stale or sold-out items. |
| Ordering → Dispatch | **Async event** (`OrderReadyForPickup` published to message broker) | Dispatch does not block order confirmation; job assignment can proceed seconds later. Decoupling here lets Dispatch scale independently during peak demand. |
| Ordering → Notifications | **Async event** (`OrderStatusChanged`) | Notifications are fire-and-forget; a slow SMS SaaS must not stall the order state machine. At-least-once delivery with idempotent template rendering is sufficient. |
| Dispatch → Notifications | **Async event** (`CourierEtaUpdated`, `DeliveryCompleted`) | Same rationale: ETA pushes are best-effort; the Notifications context consumes courier events and renders them to the appropriate channel. |
| Catalogue → Notifications | **Async event** (`MenuItemRestocked`) | Low-frequency, informational; no upstream context depends on this outcome. |
| Payment → Ordering | **Async event** (`PaymentCaptured`, `PaymentFailed`)  for post-auth capture flows | After authorisation (sync), final capture confirmation arrives asynchronously, allowing Ordering to close the lifecycle without blocking. |

---

## Conway's Law — What One Team Predicts

Conway's Law states that the communication structure of an organisation is mirrored in the architecture it produces. If a single cross-functional team owns all five contexts — Ordering, Catalogue, Payment, Dispatch, and Notifications — the likely outcome is a **modular monolith at best, a big-ball-of-mud at worst**. With no team boundary enforcing the seam between, say, Payment and Ordering, engineers will routinely take shortcuts: calling `PaymentService.charge()` directly from `OrderService.checkout()` with a concrete import (exactly the `OrderServiceTight` antipattern illustrated in `example1_flexibility_coupling_citybite.py`). Domain language bleeds across modules — a `payment_status` column quietly appears in the `orders` table because it is "just one join." Over time, the team ships faster locally but every significant change — extracting Payment into a separate service, swapping the payments gateway, or scaling Dispatch independently — requires understanding the entire codebase. This is how CityBite ends up with the shared schema pain described in the baseline: one Postgres schema that slows all five teams because nobody enforced the "database per context" rule while the codebase was still small enough to change cheaply.

---
