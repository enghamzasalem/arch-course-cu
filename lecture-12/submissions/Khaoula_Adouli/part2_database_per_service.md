# Part 2.1: Database per Service (Paper Design) — CityBite

**Rule:** No **cross-context SQL joins** after split. Each bounded context owns its datastore (logical schema); integration is via **API** or **event**.

---

## Context A — **Ordering** (logical schema)

**Tables (names only):**

- `orders`
- `order_line_items`
- `order_status_history`
- `checkout_idempotency_keys`

**Owns:** Order lifecycle, cart snapshot references (denormalized catalog line at order time if needed).

---

## Context B — **Billing & Payments** (logical schema)

**Tables (names only):**

- `payment_intents`
- `captures`
- `refunds`
- `ledger_entries`

**Owns:** Money authorization/capture, reconciliation identifiers, payout batches.

---

## One query you lose after split — and how you replace it

**Lost query (monolith era):**

```sql
SELECT o.id, o.status, p.state AS payment_state, p.amount_cents
FROM orders o
JOIN payment_intents p ON p.order_id = o.id
WHERE o.customer_id = $1
ORDER BY o.created_at DESC
LIMIT 50;
```

This **joins** Ordering and Billing in one database.

**Replacement options:**

1. **API aggregation (BFF):** `GET /customers/{id}/orders-with-payment-summary` composes two calls: Ordering list + Billing summaries by `order_id` list (bounded batch size, caching).
2. **Read model (CQRS):** Subscribe to `OrderPlaced`, `PaymentCaptured` events; project into `customer_order_read_model` owned by a **read** service or module.
3. **Denormalized pointer:** At checkout, persist `payment_intent_id` on `orders` for correlation only—Billing remains authoritative for payment state; no join across DBs, only keyed lookup.

---

## RPO / RTO intuition — Billing with async replication (Lecture 11 link)

If Billing uses **async read replicas** for reporting and dispute lookup:

- **RPO (Recovery Point Objective):** Non-zero—replica may lag **seconds to minutes** behind primary; a disaster failover could lose the most recent async commits not yet replicated (bounded by replication lag policy).
- **RTO (Recovery Time Objective):** Minutes to hours—promote replica or restore from backup, then replay WAL/event backlog depending on provider.

**Intuition:** Async replication improves read scale and availability story, but **consistency** is **eventual** on replicas; critical money paths should still read **primary** or use explicit consistency modes where required.
