# Part 1.1: Bounded Context Map & Conway’s Law — CityBite

## Bounded contexts (business-aligned)

### 1. **Ordering**

| Item | Description |
|------|-------------|
| **Ubiquitous language** | Order, line item, cart, checkout, placement, cancellation window, order status |
| **Primary user** | Customer (mobile/web) |
| **Owns** | Order aggregate lifecycle, idempotency keys for checkout, correlation to payment intent |

---

### 2. **Restaurant Catalog & Availability**

| Item | Description |
|------|-------------|
| **Ubiquitous language** | Menu, SKU, modifier, price book, opening hours, kitchen pause, out-of-stock |
| **Primary user** | Restaurant (tablet) + read-only customer views |
| **Owns** | Menu structure, pricing rules visible at order time, availability flags |

---

### 3. **Dispatch & Fulfillment**

| Item | Description |
|------|-------------|
| **Ubiquitous language** | Courier assignment, ETA, pickup, drop-off, route segment, delivery proof |
| **Primary user** | Dispatch dashboard + courier app |
| **Owns** | Assignment decisions, delivery state machine, location stream references (not raw map tiles) |

---

### 4. **Billing & Payments**

| Item | Description |
|------|-------------|
| **Ubiquitous language** | Payment intent, capture, refund, platform fee, payout, chargeback |
| **Primary user** | Customer + finance ops |
| **Owns** | Money movement orchestration, reconciliation with PSP, audit trail |

---

### 5. **Notifications**

| Item | Description |
|------|-------------|
| **Ubiquitous language** | Notification template, channel preference, delivery receipt, quiet hours |
| **Primary user** | Customer + restaurant (transactional alerts) |
| **Owns** | Outbound message fan-out, provider-specific adapters, retry policy |

---

## Integration between adjacent context pairs

| Pair | Integration style | Why |
|------|-------------------|-----|
| Ordering ↔ Catalog | **Sync API** (read) | Customer checkout must see **current** price and availability before commit; short-lived consistency matters. |
| Ordering ↔ Billing | **Sync API** + async completion | Authorize/capture must be **ordered** with order commit; webhooks from PSP can complete asynchronously. |
| Ordering ↔ Dispatch | **Async event** (`OrderPlaced`, `OrderReadyForPickup`) | Dispatch can lag seconds without blocking checkout; scales with courier pool. |
| Dispatch ↔ Notifications | **Async event** | ETA updates and “on the way” should not block dispatch writes. |
| Billing ↔ Notifications | **Async event** | Receipts and refund confirmations tolerate eventual delivery. |
| Catalog ↔ Dispatch | **Batch** (optional) | Precomputed “busy kitchen” hints for ETA; not on critical checkout path. |

---

## Conway’s Law (one paragraph)

**Conway’s Law** says system structure mirrors communication structure. If **one** team owns Ordering, Catalog, Dispatch, Billing, and Notifications, the delivered architecture will tend toward a **modular monolith** or a **tightly coupled “microlith”** with shared database and shared release trains—because coordination is cheap inside one team. That is not automatically wrong for CityBite’s **current** size: it can preserve correctness and speed. The risk is **accidental coupling** (shared tables, shared DTOs) that later blocks extraction. To stay flexible, the single team should still enforce **context boundaries in code** (modules, ports/adapters, no cross-context SQL) so a future split is possible without a big-bang rewrite.
