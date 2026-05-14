# Task 1.1: Bounded context map

## Bounded Contexts

### 1. Ordering Context

| Attribute | Detail |
|-----------|--------|
| **Ubiquitous language** | `Order`, `Cart`, `LineItem`, `OrderStatus`, `Checkout`, `OrderConfirmation` |
| **Primary user** | Customer placing a food order |
| **Owns** | Order lifecycle state machine, cart contents, order history, checkout orchestration |

---

### 2. Payment Context

| Attribute | Detail |
|-----------|--------|
| **Ubiquitous language** | `PaymentIntent`, `Charge`, `Refund`, `PaymentMethod`, `TransactionLedger`, `AuthorisationCode` |
| **Primary user** | Internal (called by Ordering); finance team for reconciliation |
| **Owns** | Payment processing, refund logic, transaction records, gateway integration |

---

### 3. Dispatch Context

| Attribute | Detail |
|-----------|--------|
| **Ubiquitous language** | `Delivery`, `Courier`, `Route`, `ETA`, `PickupWindow`, `DispatchZone` |
| **Primary user** | Courier app, operations team |
| **Owns** | Courier assignment, routing, ETA calculation, delivery status |

---

### 4. Restaurant Context

| Attribute | Detail |
|-----------|--------|
| **Ubiquitous language** | `Menu`, `MenuItem`, `Availability`, `PrepTime`, `KitchenTicket`, `RestaurantProfile` |
| **Primary user** | Restaurant staff via the restaurant portal |
| **Owns** | Menu catalogue, item availability, preparation time estimates, kitchen ticket lifecycle |

---

### 5. Notification Context

| Attribute | Detail |
|-----------|--------|
| **Ubiquitous language** | `Notification`, `Channel` (SMS/push/email), `Template`, `DeliveryReceipt`, `Preference` |
| **Primary user** | Customer and courier (recipients); other contexts (producers) |
| **Owns** | Message templating, channel routing, delivery receipts, user notification preferences |

---

## Integration Styles Between Contexts

| Context A | Context B | Style | Why |
|-----------|-----------|-------|-----|
| Ordering | Payment | **Sync API** (HTTPS) | Checkout must know immediately whether payment succeeded or failed before confirming the order to the customer. A failed async payment with an already-confirmed order creates a bad UX and reconciliation headaches. |
| Ordering | Restaurant | **Async event** (`OrderPlaced` event on queue) | The restaurant does not need to respond synchronously. Decoupling here means a slow kitchen portal cannot block checkout. The restaurant consumes the event and creates a `KitchenTicket` in its own context. |
| Ordering | Dispatch | **Async event** (`OrderConfirmed` event) | Courier assignment happens after payment succeeds and the restaurant acknowledges. There is no need for Ordering to wait — it fires the event and moves on. |
| Ordering | Notification | **Async event** (`OrderStatusChanged` event) | Notifications are fire-and-forget. A failed SMS must not roll back an order. The Notification context subscribes to status events and handles retries independently. |
| Dispatch | Notification | **Async event** (`CourierAssigned`, `DeliveryUpdated`) | ETA updates and courier location changes are high-frequency and non-blocking. Notification subscribes and fans out to the customer. |
| Restaurant | Notification | **Async event** (`OrderReadyForPickup`) | Same reasoning as Dispatch — the restaurant signals readiness; Notification handles the customer-facing message. |
| Dispatch | Restaurant | **Sync API** (read-only) | Dispatch needs the restaurant's address and pickup window to plan routing. This is a read-only call that is acceptable as sync. |

---

## Conway's Law — One Team for All Contexts

If CityBite keeps a single cross-functional team responsible for all five contexts, Conway's Law predicts that the architecture will mirror the team's communication structure: a **monolith with blurred boundaries**. Because everyone sits in the same planning meetings and shares the same codebase, there is no organisational pressure to enforce context boundaries. Developers will take shortcuts such as a Dispatch engineer will add a direct SQL join against the Orders table because it is faster than building an API, a Payment engineer will reach into the Restaurant schema to check menu prices, and so on. Over time, the "bounded contexts" exist only in documentation while the actual code is a tightly coupled ball of mud. The architecture reflects the team: one team, one system, one shared database, one deployment unit. To get the architecture described in this document, CityBite needs teams that are aligned to contexts, a Payments team, a Dispatch team, a Restaurant team, each with end-to-end ownership of their context's code, data, and API contracts. The architecture will then naturally follow the team boundaries, as Conway's Law predicts.
