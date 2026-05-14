# Part 2: Data, APIs, Sagas
## Task 2.1: Database per Service (Paper Design)

## 1. Overview
CityBite should move toward **database per service** so that each bounded context owns its own data and schema. Services may collaborate through APIs or events, but they should not depend on cross-context SQL joins or direct table access. This keeps boundaries real, reduces coupling, and allows each team to evolve its schema independently.

---

## 2. Context 1: Ordering Context

### Logical schema
**Database:** `ordering_db`

**Tables:**
- `orders`
- `order_items`
- `carts`
- `cart_items`
- `order_events`

### What it owns
The Ordering context owns cart-to-order conversion, order state transitions, and the customer-facing order lifecycle.

---

## 3. Context 2: Payments Context

### Logical schema
**Database:** `payments_db`

**Tables:**
- `payment_intents`
- `payment_transactions`
- `refunds`
- `payment_attempts`
- `payment_events`

### What it owns
The Payments context owns authorization, capture, refunds, retries, and payment audit history.

---

## 4. Query Lost After Splitting Databases

### Query that is no longer allowed
A direct SQL join such as:
- “Show each order with its payment status and refund status in one query”

This query disappears once Ordering and Payments live in separate databases.

### Replacement
CityBite can replace this with one of the following:
- **API aggregation**: a read API fetches order data from Ordering and payment data from Payments and combines them.
- **Read model**: a denormalized projection stores order + payment status together for dashboard use.
- **Event-driven projection**: Ordering publishes `OrderPlaced` and Payments publishes `PaymentAuthorized` / `PaymentFailed`, and a reporting service builds a combined view.

For user-facing screens, a read model is usually the cleanest replacement because it avoids cross-service joins at request time.

---

## 5. RPO / RTO Intuition with Async Replication

If `ordering_db` uses asynchronous replication, the **RPO** is not zero. In practical terms, if the primary fails, CityBite may lose the last few seconds of order writes that were not yet replicated. The **RTO** should be short, ideally a few minutes, because the service should fail over to a replica or restored primary quickly. This is acceptable for many read-heavy or less critical views, but the team must be honest that async replication trades a little data loss risk for better performance and availability.

---

## 6. Summary
Database per service gives CityBite real ownership boundaries. Ordering and Payments can evolve independently, and the system no longer depends on cross-context joins. The main cost is that combined views must be rebuilt through APIs, read models, or events instead of direct SQL.
